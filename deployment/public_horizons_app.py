"""Single-page display-only Render entry point for Forecast Horizons."""

import json
import os

import streamlit as st

from deployment.public_horizons_gate import load_approved_pilot
from deployment.validate_public_data_package import DATA_DIR, REGISTRY
from release_policy import PUBLIC_HOLD


def main():
    st.set_page_config(page_title="Warehouse IQ · Forecast Horizons", layout="wide")
    payload = load_approved_pilot(os.environ)
    if payload is None:
        st.title("Forecast Horizons")
        st.info(PUBLIC_HOLD)
        st.stop()

    from design_system import apply_global_theme
    from forecast_horizons import render_forecast_horizons
    from forecast_horizons_data import prepare_forecast_horizons
    from product_layout import apply_product_theme, workspace_header
    from research_overview_data import read_pinned_csv

    registry = json.loads(payload[REGISTRY])["artifacts"]
    scores, origins = (
        read_pinned_csv(payload[f"{DATA_DIR}/{registry[name]['path']}"], registry[name])
        for name in ("scores", "origins")
    )

    def load_data(dataset):
        return prepare_forecast_horizons(dataset, scores, origins)

    apply_global_theme()
    apply_product_theme()
    workspace_header("Forecast Horizons", "Final Research · Retail forecasting", include_downloads=False)
    render_forecast_horizons(include_downloads=False, load_data=load_data, registry=registry)
    st.caption(
        "Capstone analysis by Hyuntae Park. "
        "M5 data credits the University of Nicosia, Makridakis Open Forecasting Center and Walmart. "
        "Corporación Favorita data credits Alexis Cook, DanB, inversion and Ryan Holbrook."
    )
    st.markdown(
        "[M5 competition](https://www.kaggle.com/competitions/m5-forecasting-accuracy) · "
        "[M5 results paper](https://doi.org/10.1016/j.ijforecast.2021.11.013) · "
        "[Favorita 2021 competition](https://www.kaggle.com/competitions/store-sales-time-series-forecasting)"
    )


if __name__ == "__main__":
    main()
