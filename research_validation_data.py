"""Validate saved inference and coverage without generating new statistics."""

from deployment.analytics_access import data_path, retail_datasets, selected

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loading import DataIssue, source_path
from forecast_horizons_data import prepare_forecast_horizons
from model_strategies_data import R16, prepare_strategy_study
from research_overview_data import DATASETS, EXPORT_DIRECTORY, HORIZONS, META_METHODS, SOURCE_REGISTRY, read_pinned_research_exports


FAMILY_PINS = {"V3": "v3_inference", "R19": "r19_inference"}
HOLM_COLUMNS = {"V3": "p_holm", "R19": "p_holm_primary"}
PAIR_COUNTS = {"V3": 12, "R19": 11}
BLOCKS = (2, 4)
HAS_INTERVAL = "EXPLORATORY_BLOCK_BOOTSTRAP"
INSUFFICIENT = "INSUFFICIENT_TEMPORAL_REPLICATION"
UNESTIMABLE = "UNESTIMABLE_FORECAST_PAIR"
COVERAGE_PINS = ("scores", "origins")
ELIGIBILITY_PINS = ("meta_scores", "meta_coverage")


@dataclass(frozen=True)
class ValidationStudy:
    dataset: str
    family: str
    inference: pd.DataFrame
    coverage: pd.DataFrame
    evidence: dict
    annual_meta: pd.Series | None
    unavailable_meta_scores: int

    def pairs(self):
        return list(self.inference[["method", "comparator"]].drop_duplicates().itertuples(index=False, name=None))

    def pair(self, block, pair):
        method, comparator = pair
        rows = self.inference
        return rows.loc[rows.method.eq(method) & rows.comparator.eq(comparator) & rows.block_length.eq(block)].set_index("horizon").reindex(HORIZONS)


def _validated_inference(family, frame, origin_counts):
    rows = frame.rename(columns={HOLM_COLUMNS[family]: "adjusted_p"}).copy()
    pairs = rows[["method", "comparator"]].drop_duplicates()
    if len(pairs) != PAIR_COUNTS[family] or pairs.method.eq(pairs.comparator).any():
        raise DataIssue("Unexpected comparison pairs in the saved inference family.")
    expected = {
        (dataset, horizon, method, comparator, block)
        for dataset in retail_datasets(DATASETS) for horizon in HORIZONS for block in BLOCKS
        for method, comparator in pairs.itertuples(index=False, name=None)
    }
    keys = ["dataset", "horizon", "method", "comparator", "block_length"]
    if len(rows) != len(expected) or set(rows[keys].itertuples(index=False, name=None)) != expected:
        raise DataIssue("The saved inference family has incomplete or duplicate comparison keys.")

    counts = origin_counts.set_index(["dataset", "horizon"], verify_integrity=True).nonoverlapping_origins
    row_keys = pd.MultiIndex.from_frame(rows[["dataset", "horizon"]])
    if not rows.nonoverlap_origins.eq(counts.reindex(row_keys).to_numpy()).all():
        raise DataIssue("The inference table disagrees with the verified disjoint-origin coverage.")
    supported = rows.status.eq(HAS_INTERVAL)
    unestimable = rows.status.eq(UNESTIMABLE)
    adjusted = supported & rows.block_length.eq(2)
    interval = rows[["ci_low", "ci_high", "p_approx"]]
    if not (
        rows.status.isin([HAS_INTERVAL, INSUFFICIENT, UNESTIMABLE]).all()
        and rows.difference_pp.isna().eq(unestimable).all()
        and interval.notna().eq(supported, axis="index").all().all()
        and rows.adjusted_p.notna().eq(adjusted).all()
        and np.isfinite(rows[["difference_pp", "ci_low", "ci_high"]].stack()).all()
        and rows.loc[supported, "ci_low"].le(rows.loc[supported, "ci_high"]).all()
        and rows.loc[supported, "p_approx"].between(0, 1).all()
        and rows.loc[adjusted, "adjusted_p"].between(0, 1).all()
        and rows.loc[adjusted, "adjusted_p"].ge(rows.loc[adjusted, "p_approx"]).all()
    ):
        raise DataIssue("A saved estimate, confidence interval, or Holm status is inconsistent.")
    enough = rows.nonoverlap_origins.ge(12) & (rows.nonoverlap_origins // rows.block_length).ge(6)
    if (supported & ~enough).any():
        raise DataIssue("An interval is present without the protocol's required temporal replication.")
    effects = rows.pivot(index=keys[:-1], columns="block_length", values="difference_pp")
    if not effects[2].equals(effects[4]):
        raise DataIssue("Block sensitivity changed a frozen paired point effect.")
    return rows


def _read_evidence(directory: Path) -> dict:
    pin = json.loads(data_path("research_overview_sources.json", SOURCE_REGISTRY).read_bytes())["artifacts"]["validation_evidence"]
    path = source_path(data_path("final_research_exports", directory), pin["path"])
    content = path.read_bytes()
    if hashlib.sha256(content).hexdigest() != pin["sha256"]:
        raise DataIssue("Evidence receipt hash mismatch. Restore the pinned local receipt.")
    value = json.loads(content)
    if len(value) != pin["rows"] or list(value) != pin["keys"]:
        raise DataIssue("Unexpected schema in the saved evidence receipt.")
    return value


def load_validation_study(dataset, family, directory: Path = EXPORT_DIRECTORY):
    if dataset not in DATASETS or family not in FAMILY_PINS:
        raise DataIssue("Choose one of the two studied retailers and inference families.")
    inference_pin = FAMILY_PINS[family]
    scoped = selected("dataset") is not None
    names = (inference_pin, *COVERAGE_PINS) if scoped else (inference_pin, *COVERAGE_PINS, *ELIGIBILITY_PINS)
    tables = read_pinned_research_exports(names, directory)
    ridge = prepare_forecast_horizons(dataset, tables["scores"], tables["origins"])
    rows = _validated_inference(family, tables[inference_pin], tables["origins"])
    if scoped:
        return ValidationStudy(dataset, family, rows.loc[rows.dataset.eq(dataset)].copy(), ridge.coverage,
                               {}, None, 0)
    meta = prepare_strategy_study("Favorita", R16, tables)
    return ValidationStudy(
        dataset, family, rows.loc[rows.dataset.eq(dataset)].copy(), ridge.coverage,
        _read_evidence(directory), meta.eligibility.loc[52], int(meta.wape.loc[list(META_METHODS), 52].isna().sum()),
    )
