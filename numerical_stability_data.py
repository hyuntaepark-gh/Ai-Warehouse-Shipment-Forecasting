"""Read the pinned full-cohort ablations and the separate matched correction."""

from deployment.analytics_access import data_path, retail_datasets

from dataclasses import dataclass
import json
from math import isclose, isfinite
from pathlib import Path

import pandas as pd

from data_loading import DataIssue
from forecast_horizons_data import prepare_forecast_horizons
from research_overview_data import (
    COMPONENTS, DATASETS, EXPORT_DIRECTORY, HORIZONS, METHODS, SOURCE_REGISTRY, read_pinned_research_exports,
)


MODE = dict(zip(METHODS, ("Direct", "Recursive")))
CONTROL = "FullControl"
CORRECTION = "V1 → V2 correction"
SOURCES = ("ablations", "matched", "scores", "origins")


@dataclass(frozen=True)
class Comparison:
    baseline: float | None
    selected: float | None = None
    delta_pp: float | None = None


@dataclass(frozen=True)
class StabilityData:
    dataset: str
    horizon: int
    method: str
    cases: int | None
    origins: int
    disjoint: int
    ablations: pd.DataFrame
    correction_row: pd.DataFrame
    comparisons: dict[str, Comparison]


def _close(left, right):
    # The frozen exports round to significant digits. Use the Phase 1.5 audit tolerance.
    return isclose(left, right, rel_tol=1e-9, abs_tol=1e-8)


def _ablation_scores(row, reference, cases, baseline):
    if pd.isna(row.status) or row.status != "COMPLETE" or baseline is None or cases is None:
        return None
    fields = [
        "reference", "complete_rows", "failed_rows", "successful_fraction", "full_cohort_WAPE",
        "matched_success_only_WAPE", "reference_matched_WAPE", "delta_matched_pp", "full_cohort_delta_pp",
    ]
    if row[fields].isna().any():
        return None
    if (row.reference != reference or row.complete_rows != cases
            or row.failed_rows != 0 or row.successful_fraction != 1):
        raise DataIssue("A full-cohort ablation does not match its Ridge reference and coverage.")
    value, delta = float(row.full_cohort_WAPE), float(row.full_cohort_delta_pp)
    if not isfinite(value) or value < 0 or not (
        _close(row.reference_matched_WAPE, baseline)
        and _close(row.matched_success_only_WAPE, value)
        and _close(row.delta_matched_pp, delta)
        and _close(delta, value - baseline)
        and isfinite(delta)
    ):
        raise DataIssue("A full-cohort ablation conflicts with the matched WAPE metrics.")
    return value, delta


def _matched_correction(rows, cases, baseline, prior_run):
    if rows.empty or rows.iloc[0].isna().any() or cases is None or baseline is None:
        return Comparison(None)
    row = rows.iloc[0]
    if row.prior_run != prior_run or row.matched_complete_rows != cases:
        raise DataIssue("The original and stabilized comparison does not match the pinned run and coverage.")
    if not (
        isfinite(row.V1_WAPE) and row.V1_WAPE >= 0 and _close(row.V2_WAPE, baseline)
        and _close(row.V1_minus_V2_pp, row.V1_WAPE - row.V2_WAPE)
    ):
        raise DataIssue("The original and stabilized WAPE values do not match the saved correction.")
    return Comparison(float(row.V1_WAPE), float(row.V2_WAPE), float(-row.V1_minus_V2_pp))


def prepare_numerical_stability(dataset, horizon, method, tables, prior_run):
    if dataset not in DATASETS or horizon not in HORIZONS or method not in METHODS:
        raise DataIssue("Choose a studied retailer, horizon, and Ridge strategy.")
    v2 = prepare_forecast_horizons(dataset, tables["scores"], tables["origins"])
    reference = v2.scores.loc[(horizon, method)]
    cases = None if pd.isna(reference.store_weeks) else int(reference.store_weeks)
    baseline = None if pd.isna(reference.wape) else float(reference.wape)
    coverage = v2.coverage.loc[horizon]

    labels = {f"{MODE[method]}_{component}": component for component in COMPONENTS}
    source = tables["ablations"]
    rows = source.loc[source.dataset.eq(dataset) & source.horizon.eq(horizon) & source.method.isin(labels)]
    ablations = rows.assign(component=rows.method.map(labels)).set_index("component", verify_integrity=True)
    scored = {
        component: _ablation_scores(row, method, cases, baseline)
        for component, row in ablations.iterrows()
    }
    control = scored.get(CONTROL)
    if control is not None and (control[0] != baseline or control[1] != 0):
        raise DataIssue("FullControl does not reproduce the pinned V2 baseline.")
    comparisons = {}
    for component in COMPONENTS[1:]:
        variant = scored.get(component)
        comparisons[component] = (
            Comparison(control[0], *variant) if control is not None and variant is not None
            else Comparison(control[0] if control is not None else None)
        )
    ablations = ablations.reindex(COMPONENTS)
    ablations["comparison_available"] = [
        control is not None and scored.get(component) is not None for component in COMPONENTS
    ]

    source = tables["matched"]
    matched = source.loc[source.dataset.eq(dataset) & source.horizon.eq(horizon) & source.method.eq(method)]
    if len(matched) > 1:
        raise DataIssue("More than one saved correction matches the selected Ridge evaluation.")
    comparisons[CORRECTION] = _matched_correction(matched, cases, baseline, prior_run)
    return StabilityData(
        dataset, horizon, method, cases, int(coverage.overlapping_origins), int(coverage.nonoverlapping_origins),
        ablations.reset_index(), matched, comparisons,
    )


def load_numerical_stability(horizon, method, directory: Path = EXPORT_DIRECTORY):
    tables = read_pinned_research_exports(SOURCES, directory)
    registry = json.loads(data_path("research_overview_sources.json", SOURCE_REGISTRY).read_text(encoding="utf-8"))["artifacts"]
    prior_run = registry["matched"]["prior_run_id"]
    return {
        dataset: prepare_numerical_stability(dataset, horizon, method, tables, prior_run)
        for dataset in retail_datasets(DATASETS)
    }
