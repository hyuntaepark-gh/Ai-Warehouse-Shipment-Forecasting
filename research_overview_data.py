"""Read the pinned aggregate exports for the final retail research overview."""

from deployment.analytics_access import data_path

from dataclasses import dataclass
import hashlib
from io import BytesIO
import json
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from data_loading import DataIssue, ROOT, source_path


DATASETS = ("M5", "Favorita")
HORIZONS = (1, 4, 12, 26, 52)
METHODS = ("DirectRidge", "RecursiveRidge")
COMPONENTS = ("FullControl", "NoLog", "NoStoreScale", "NoStandardization", "NoUpperCap")
META_METHODS = ("MetaHardClassifier", "MetaLossBlend")
OVERVIEW_SOURCES = ("scores", "origins", "matched", "ablations", "meta_scores", "meta_coverage", "strategies")
EXPORT_DIRECTORY = ROOT / "final_research_exports"
SOURCE_REGISTRY = ROOT / "research_overview_sources.json"


@dataclass(frozen=True)
class ResearchOverviewData:
    horizon_wape: pd.DataFrame
    origins: pd.DataFrame
    matched: pd.DataFrame
    ablations: pd.DataFrame
    convex_annual_wape: float
    meta_annual: pd.DataFrame
    meta_development: pd.Series


@st.cache_data(show_spinner=False, max_entries=24)
def _parse_csv(data):
    return pd.read_csv(BytesIO(data), float_precision="round_trip")


def _read_export(directory, pin):
    path = source_path(data_path("final_research_exports", directory), pin["path"])
    return read_pinned_csv(path.read_bytes(), pin)


def read_pinned_csv(data, pin):
    """Apply the same frozen CSV contract to file reads and hosted bytes."""
    name = Path(pin["path"]).name
    if hashlib.sha256(data).hexdigest() != pin["sha256"]:
        raise DataIssue(f"Hash mismatch for {name}. Restore the pinned local export.")
    frame = _parse_csv(data)
    if len(frame) != pin["rows"] or list(frame.columns) != pin["columns"]:
        raise DataIssue(f"Unexpected schema or row count in {name}.")
    return frame


def _is_score(series):
    return bool(np.isfinite(series).all() and series.ge(0).all())


def read_pinned_research_exports(names, directory=EXPORT_DIRECTORY):
    """Read only the requested artifacts, in the registry's original schema."""
    registry = json.loads(data_path("research_overview_sources.json", SOURCE_REGISTRY).read_text(encoding="utf-8"))["artifacts"]
    return {name: _read_export(directory, registry[name]) for name in names}


def load_research_overview(dataset: str, directory: Path = EXPORT_DIRECTORY) -> ResearchOverviewData:
    if dataset not in DATASETS:
        raise DataIssue("Choose M5 or Favorita for the final research overview.")
    tables = {
        name: frame.loc[frame.dataset.eq(dataset)].copy()
        for name, frame in read_pinned_research_exports(OVERVIEW_SOURCES, directory).items()
    }

    scores = tables["scores"].loc[lambda f: f.scope.eq("complete_all_origins") & f.method.isin(METHODS)]
    horizon_wape = scores.pivot(index="horizon", columns="method", values="wape").reindex(columns=METHODS)
    if tuple(horizon_wape.index) != HORIZONS or not _is_score(horizon_wape.stack()) or horizon_wape.isna().any().any():
        raise DataIssue("Expected both Ridge scores at all five horizons in the complete cohort.")

    origins = tables["origins"].set_index("horizon", verify_integrity=True).sort_index()
    if tuple(origins.index) != HORIZONS or not (
        origins.nonoverlapping_origins.gt(0) & origins.nonoverlapping_origins.le(origins.overlapping_origins)
    ).all():
        raise DataIssue("Expected valid origin counts for each of the five horizons.")
    for method in METHODS:
        scored = scores.loc[scores.method.eq(method)].set_index("horizon")
        if not scored.origins.reindex(origins.index).eq(origins.overlapping_origins).all():
            raise DataIssue("The horizon scores and origin counts describe different cohorts.")

    matched = tables["matched"].loc[lambda f: f.horizon.eq(52) & f.method.isin(METHODS)]
    matched = matched.set_index("method", verify_integrity=True).reindex(METHODS)
    if not _is_score(matched.V1_WAPE) or not matched.V2_WAPE.eq(horizon_wape.loc[52]).all():
        raise DataIssue("The matched 52-week comparison does not align with the V2 horizon scores.")

    ablations = tables["ablations"].loc[lambda f: f.horizon.eq(52)].copy()
    ablations[["mode", "component"]] = ablations.method.str.split("_", n=1, expand=True)
    ablations = ablations.pivot(index="component", columns="mode", values="full_cohort_WAPE")
    ablations = ablations.reindex(index=COMPONENTS, columns=("Direct", "Recursive"))
    if not _is_score(ablations.stack()) or ablations.isna().any().any() or not np.array_equal(
        ablations.loc["FullControl"].to_numpy(), horizon_wape.loc[52].to_numpy()
    ):
        raise DataIssue("Expected verified 52-week ablations with a control matching the V2 scores.")

    meta_annual = tables["meta_scores"].loc[lambda f: f.horizon.eq(52) & f.method.isin(META_METHODS)]
    meta_annual = meta_annual.set_index("method", verify_integrity=True).reindex(META_METHODS)
    meta_development = tables["meta_coverage"].set_index("horizon", verify_integrity=True).loc[52]
    estimable = meta_development.status == "ESTIMABLE"
    expected_status = "SCORED" if estimable else meta_development.status
    if not meta_annual.status.eq(expected_status).all() or not meta_annual.pooled_WAPE.notna().eq(estimable).all():
        raise DataIssue("The saved meta scores do not agree with development eligibility.")
    strategies = tables["strategies"].set_index("horizon", verify_integrity=True)
    if not _is_score(strategies.DevConvexBlend):
        raise DataIssue("Expected finite WAPE for the saved development-tuned combination.")
    return ResearchOverviewData(
        horizon_wape, origins, matched, ablations, float(strategies.loc[52, "DevConvexBlend"]),
        meta_annual, meta_development,
    )
