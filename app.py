"""Supply Chain Analytics | historical capstone presentation, version 1."""
import importlib

# Discover local modules added while the Streamlit server is running.
importlib.invalidate_caches()

import streamlit as st
from design_system import apply_global_theme, page_intro
from navigation import (
    FORECAST_HORIZONS, LABELS, MODEL_STRATEGIES, NUMERICAL_STABILITY, RESEARCH_OVERVIEW, RESEARCH_ROUTES, RESEARCH_VALIDATION,
    render_navigation,
)
from product_layout import apply_product_theme, workspace_header
from release_policy import PUBLIC_HOLD, public_data_blocked

st.set_page_config(page_title="Warehouse IQ · Demand Intelligence", page_icon="📦", layout="wide")

apply_global_theme()
apply_product_theme()

page = render_navigation()

if public_data_blocked(st.get_option("server.address")):
    st.title(LABELS[page])
    st.info(PUBLIC_HOLD)
    st.stop()

from overview import render_overview
from historical import render_historical
from model_comparison import render_model_comparison
from warehouse import render_warehouse
from model_validation import render_validation
from future_forecasting import render_future
from operational_insights import render_operational
from data_foundation import render_foundation
from research_overview import render_research_overview
from forecast_horizons import render_forecast_horizons
from numerical_stability import render_numerical_stability
from model_strategies import render_model_strategies
from research_validation import render_research_validation

workspace_header(LABELS[page], "Final Research · Retail forecasting" if page in RESEARCH_ROUTES
                 else "Original Warehouse Operations · Archived study")

if page not in ["Executive Overview", "Operational Insights", "Data Foundation", *RESEARCH_ROUTES]:
    page_intro(page)

if page == "Historical Demand":
    render_historical()
elif page == "Executive Overview":
    render_overview()
elif page == "Model Comparison":
    render_model_comparison()
elif page == "Warehouse Analytics":
    render_warehouse()
elif page == "Model Validation":
    render_validation()
elif page == "Future Forecasting":
    render_future()
elif page == "Data Foundation":
    render_foundation()
elif page == RESEARCH_OVERVIEW:
    render_research_overview()
elif page == FORECAST_HORIZONS:
    render_forecast_horizons()
elif page == NUMERICAL_STABILITY:
    render_numerical_stability()
elif page == MODEL_STRATEGIES:
    render_model_strategies()
elif page == RESEARCH_VALIDATION:
    render_research_validation()
else:
    render_operational()
