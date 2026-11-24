"""Align the final retail horizon cohorts without imputing missing scores."""

from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd

from data_loading import DataIssue
from research_overview_data import DATASETS, EXPORT_DIRECTORY, HORIZONS, METHODS, read_pinned_research_exports


SCOPE = "complete_all_origins"
METRICS = {"wape": "Pooled WAPE", "mean_origin_wape": "Mean origin WAPE"}
ORIGINS = ("overlapping_origins", "nonoverlapping_origins")
COUNTS = ("origins", "stores", "store_weeks")


@dataclass(frozen=True)
class ForecastHorizonData:
    dataset: str
    scores: pd.DataFrame
    coverage: pd.DataFrame
    annual_disjoint: pd.Series

    def metric(self, column):
        return self.scores[column].unstack("method").reindex(columns=METHODS)

    def table(self):
        return (
            self.scores.reset_index()
            .merge(self.coverage.reset_index(), on="horizon", validate="many_to_one")
            .assign(dataset=self.dataset, scope=SCOPE)
            [["dataset", "scope", "horizon", "method", *METRICS, *COUNTS, *ORIGINS]]
        )


def _positive_counts(frame):
    values = frame.to_numpy(dtype=float)
    return bool(np.isfinite(values).all() and (values > 0).all() and (values % 1 == 0).all())


def prepare_forecast_horizons(dataset: str, scores: pd.DataFrame, origins: pd.DataFrame) -> ForecastHorizonData:
    if dataset not in DATASETS:
        raise DataIssue("Choose M5 or Favorita for the final retail study.")
    coverage = origins.loc[origins.dataset.isin(DATASETS), ["dataset", "horizon", *ORIGINS]]
    coverage = coverage.set_index(["dataset", "horizon"], verify_integrity=True)
    keys = pd.MultiIndex.from_product([DATASETS, HORIZONS], names=["dataset", "horizon"])
    if set(coverage.index) != set(keys) or not _positive_counts(coverage):
        raise DataIssue("The coverage export must report origin counts for both retailers and all five horizons.")
    if coverage.nonoverlapping_origins.gt(coverage.overlapping_origins).any():
        raise DataIssue("Disjoint origin counts exceed all scored origins.")

    selected = scores.loc[scores.dataset.eq(dataset) & scores.scope.eq(SCOPE) & scores.method.isin(METHODS),
                          ["horizon", "method", *METRICS, *COUNTS]]
    if not selected.horizon.isin(HORIZONS).all():
        raise DataIssue("A Ridge score has an unexpected forecast horizon.")
    selected = selected.set_index(["horizon", "method"], verify_integrity=True)
    for column in METRICS:
        selected[column] = pd.to_numeric(selected[column], errors="raise")
        finite = selected[column].dropna()
        if not np.isfinite(finite).all() or finite.lt(0).any():
            raise DataIssue("WAPE must be a finite, nonnegative value or an unavailable score.")
    if not _positive_counts(selected[list(COUNTS)]):
        raise DataIssue("The selected score rows must report positive integer cohort counts.")

    study_coverage = coverage.loc[dataset].reindex(HORIZONS)
    if not selected.origins.eq(study_coverage.overlapping_origins.reindex(
        selected.index.get_level_values("horizon")
    ).to_numpy()).all():
        raise DataIssue("Scored origins do not match the coverage export.")
    if selected.groupby(level="horizon")[list(COUNTS)].nunique().gt(1).any().any():
        raise DataIssue("Direct and Recursive Ridge do not share the same scored cohort.")

    index = pd.MultiIndex.from_product([HORIZONS, METHODS], names=["horizon", "method"])
    return ForecastHorizonData(
        dataset, selected.reindex(index), study_coverage, coverage.xs(52, level="horizon").nonoverlapping_origins,
    )


def load_forecast_horizons(dataset: str, directory: Path = EXPORT_DIRECTORY) -> ForecastHorizonData:
    tables = read_pinned_research_exports(("scores", "origins"), directory)
    return prepare_forecast_horizons(dataset, tables["scores"], tables["origins"])
