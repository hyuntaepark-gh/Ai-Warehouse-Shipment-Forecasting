"""Keep the V3 benchmark and the R16 adapted comparators in separate cohorts."""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from data_loading import DataIssue
from forecast_horizons_data import prepare_forecast_horizons
from research_overview_data import DATASETS, EXPORT_DIRECTORY, HORIZONS, META_METHODS, METHODS, read_pinned_research_exports


V3 = "V3"
R16 = "R16"
REFERENCES = ("HorizonOnly", "HorizonRegime", "EqualWeight", "SeasonalBlend", "DevConvexBlend")
PROTOCOL_METHODS = {
    V3: (*REFERENCES, "DirectPooledHGB", *METHODS),
    R16: (*META_METHODS, *REFERENCES),
}
SOURCES = {
    V3: ("strategies", "ablations", "scores", "origins"),
    R16: ("meta_scores", "meta_coverage", "scores", "origins"),
}
SCORED = "SCORED"
NO_RESULT = "NOT_AVAILABLE"
INSUFFICIENT = "NOT_ESTIMABLE_INSUFFICIENT_DEVELOPMENT_WINDOWS"


@dataclass(frozen=True)
class StrategyStudy:
    dataset: str
    protocol: str
    wape: pd.DataFrame
    status: pd.DataFrame
    coverage: pd.DataFrame
    annual_disjoint: pd.Series
    eligibility: pd.DataFrame | None = None

    def difference(self, horizon, strategy, reference):
        value, base = self.wape.loc[[strategy, reference], horizon]
        return None if pd.isna(value) or pd.isna(base) else float(value - base)

    def table(self):
        metrics = self.wape.rename_axis(index="method", columns="horizon").stack(future_stack=True).rename("pooled_WAPE")
        status = self.status.rename_axis(index="method", columns="horizon").stack(future_stack=True).rename("status")
        return (
            pd.concat([metrics, status], axis=1).reset_index()
            .merge(self.coverage.reset_index(), on="horizon", validate="many_to_one")
            .assign(dataset=self.dataset, protocol=self.protocol)
        )[["dataset", "protocol", "horizon", "method", "pooled_WAPE", "status",
           "complete_store_weeks", "evaluated_origins", "disjoint_origins"]]


def _by_horizon(frame, dataset):
    rows = frame.loc[frame.dataset.eq(dataset)].drop(columns="dataset").set_index("horizon", verify_integrity=True)
    if set(rows.index) != set(HORIZONS):
        raise DataIssue("Expected one record for each of the five research horizons.")
    return rows.reindex(HORIZONS)


def _v3_scores(dataset, tables, ridge, coverage):
    paper = _by_horizon(tables["strategies"], dataset)
    controls = tables["ablations"]
    methods = dict(zip(("Direct_FullControl", "Recursive_FullControl"), METHODS))
    controls = controls.loc[controls.dataset.eq(dataset) & controls.method.isin(methods)].copy()
    controls["method"] = controls.method.map(methods)
    controls = controls.set_index(["horizon", "method"], verify_integrity=True)
    expected = ridge.scores.index
    if set(controls.index) != set(expected):
        raise DataIssue("The saved V3 Ridge controls do not cover all matched horizons.")
    controls = controls.reindex(expected)
    if not (
        controls.reference.eq(expected.get_level_values("method")).all()
        and controls.status.eq("COMPLETE").all()
        and controls.successful_fraction.eq(1).all()
        and controls.failed_rows.eq(0).all()
        and controls.complete_rows.eq(coverage.complete_store_weeks.reindex(expected.get_level_values("horizon")).to_numpy()).all()
        and controls.full_cohort_WAPE.eq(ridge.scores.wape).all()
        and controls.matched_success_only_WAPE.eq(controls.full_cohort_WAPE).all()
    ):
        raise DataIssue("V3 Ridge controls do not reproduce the pinned complete-case reference.")
    matrix = paper.join(controls.full_cohort_WAPE.unstack("method")).T.reindex(PROTOCOL_METHODS[V3])
    status = matrix.notna().replace({True: SCORED, False: NO_RESULT})
    return matrix, status


def _r16_scores(dataset, tables, coverage):
    eligible = _by_horizon(tables["meta_coverage"], dataset)
    counts = eligible.drop(columns="status").to_numpy(dtype=float)
    if not (
        np.isfinite(counts).all() and (counts >= 0).all() and (counts % 1 == 0).all()
        and eligible.minimum_development_windows.gt(0).all()
        and eligible.development_windows_total.eq(
            eligible.development_windows_eligible + eligible.incomplete_windows + eligible.nonpositive_windows
        ).all()
        and eligible.test_rows.eq(eligible.test_windows * eligible.index).all()
        and eligible.test_rows.ge(coverage.complete_store_weeks).all()
    ):
        raise DataIssue("The saved R16 eligibility or test coverage counts are inconsistent.")
    can_fit = eligible.development_windows_eligible.ge(eligible.minimum_development_windows)
    if not eligible.status.eq(np.where(can_fit, "ESTIMABLE", INSUFFICIENT)).all():
        raise DataIssue("R16 eligibility status disagrees with the development window threshold.")

    rows = tables["meta_scores"]
    rows = rows.loc[rows.dataset.eq(dataset)].set_index(["horizon", "method"], verify_integrity=True)
    index = pd.MultiIndex.from_product([HORIZONS, PROTOCOL_METHODS[R16]], names=["horizon", "method"])
    if set(rows.index) != set(index):
        raise DataIssue("The pinned R16 score grid has unexpected strategy keys.")
    rows = rows.reindex(index)
    horizon = index.get_level_values("horizon")
    counts = coverage.complete_store_weeks.reindex(horizon).to_numpy()
    scored = can_fit.reindex(horizon).to_numpy() | ~index.get_level_values("method").isin(META_METHODS)
    if not (
        rows.complete_rows.eq(counts).all()
        and rows.scored_rows.eq(np.where(scored, counts, 0)).all()
        and rows.pooled_WAPE.notna().eq(scored).all()
        and rows.status.eq(np.where(scored, SCORED, INSUFFICIENT)).all()
    ):
        raise DataIssue("R16 scores, nulls or cases disagree with the pinned complete-case and eligibility evidence.")
    return rows.pooled_WAPE.unstack("horizon"), rows.status.unstack("horizon"), eligible


def prepare_strategy_study(dataset, protocol, tables):
    if dataset not in DATASETS or protocol not in PROTOCOL_METHODS:
        raise DataIssue("Choose a studied dataset and strategy protocol.")
    ridge = prepare_forecast_horizons(dataset, tables["scores"], tables["origins"])
    cases = ridge.scores.store_weeks.unstack("method")
    if cases.isna().any().any():
        raise DataIssue("Complete case coverage is unavailable for the selected study.")
    coverage = ridge.coverage.rename(columns={
        "overlapping_origins": "evaluated_origins", "nonoverlapping_origins": "disjoint_origins",
    }).assign(complete_store_weeks=cases[METHODS[0]].astype(int))

    eligibility = None
    if protocol == V3:
        matrix, status = _v3_scores(dataset, tables, ridge, coverage)
    else:
        matrix, status, eligibility = _r16_scores(dataset, tables, coverage)
    methods = PROTOCOL_METHODS[protocol]
    matrix = matrix.reindex(index=methods, columns=HORIZONS)
    finite = matrix.stack()
    if not np.isfinite(finite).all() or finite.lt(0).any():
        raise DataIssue("Pooled WAPE must be nonnegative and finite, or unavailable.")
    return StrategyStudy(dataset, protocol, matrix, status.reindex_like(matrix), coverage, ridge.annual_disjoint, eligibility)


def load_strategy_study(dataset, protocol, directory: Path = EXPORT_DIRECTORY):
    if protocol not in SOURCES:
        raise DataIssue("Choose one of the two saved strategy protocols.")
    return prepare_strategy_study(dataset, protocol, read_pinned_research_exports(SOURCES[protocol], directory))
