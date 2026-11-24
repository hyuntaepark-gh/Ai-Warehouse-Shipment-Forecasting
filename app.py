"""Publication-gated Warehouse IQ application for the CFS Area pilot."""
import os

import streamlit as st

from design_system import apply_global_theme
from navigation import LABELS, RESEARCH_ROUTES, render_navigation
from product_layout import apply_product_theme, publication_hold
from release_policy import PUBLIC_HOLD

st.set_page_config(page_title="Warehouse IQ · Demand Intelligence", page_icon="📦", layout="wide")

apply_global_theme()
apply_product_theme()

page = render_navigation()

study = ("Final Research · M5 and Corporación Favorita retail forecasting" if page in RESEARCH_ROUTES
         else "Original Warehouse Operations · Archived order-demand study")

if page == "Data Foundation":
    from deployment.cfs_area_gate import load_approved_cfs

    cfs_payload = load_approved_cfs(os.environ)
    if cfs_payload is not None:
        from cfs_area_coverage import parse_coverage, render_coverage

        try:
            cfs_source, cfs_rows = parse_coverage(cfs_payload)
        except (ValueError, TypeError, KeyError):
            publication_hold(LABELS[page], study)
        else:
            st.title(LABELS[page])
            st.caption("Original Warehouse Operations · Federal data reference")
            render_coverage(cfs_source, cfs_rows)
            st.markdown("**Original warehouse and M5 source summaries**")
            st.info(PUBLIC_HOLD, icon=":material/lock:")
        st.stop()

publication_hold(LABELS[page], study)
