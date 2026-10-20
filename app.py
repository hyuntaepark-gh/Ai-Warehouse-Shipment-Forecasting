"""Supply Chain Analytics | historical capstone presentation, version 1."""
import importlib

# Discover local modules added while the Streamlit server is running.
importlib.invalidate_caches()

import streamlit as st
from design_system import apply_global_theme, page_intro
from navigation import render_navigation
from product_layout import apply_product_theme
from chart_access import start_data_center
from navigation import LABELS

from overview import render_overview
from historical import render_historical
from model_comparison import render_model_comparison
from warehouse import render_warehouse
from model_validation import render_validation
from future_forecasting import render_future
from operational_insights import render_operational
from data_foundation import render_foundation

st.set_page_config(page_title="Warehouse IQ · Demand Intelligence", page_icon="📦", layout="wide")

apply_global_theme()
apply_product_theme()

page = render_navigation()
start_data_center(LABELS[page])

if page not in ["Executive Overview", "Operational Insights", "Data Foundation"]:
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
else:
    render_operational()
