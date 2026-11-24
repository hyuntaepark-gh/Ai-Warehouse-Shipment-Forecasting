"""Public Warehouse IQ reports with independent evidence and visualization gates."""
import os

import streamlit as st

from deployment.analytics_access import approved_payload, evidence_scopes, render_inputs
from deployment.analytics_routes import render_original, render_section
from deployment.cfs_area_gate import load_approved_cfs
from cfs_area_coverage import parse_coverage, render_coverage
from design_system import apply_global_theme
from navigation import LABELS, RESEARCH_ROUTES, render_navigation
from product_layout import apply_product_theme
from release_policy import PUBLIC_HOLD
from reporting_intro import render_report

st.set_page_config(page_title="Warehouse IQ · Demand Intelligence", page_icon="📦", layout="wide")
apply_global_theme()
apply_product_theme()
route = render_navigation()
label = LABELS[route]
study = ("Final Research · M5 and Corporación Favorita retail forecasting" if route in RESEARCH_ROUTES
         else "Original Warehouse Operations · Archived order-demand study")

full = approved_payload(label, os.environ)
cfs = None
if route == "Data Foundation":
    cfs_payload = load_approved_cfs(os.environ)
    if cfs_payload is not None:
        try:
            cfs = parse_coverage(cfs_payload)
        except (ValueError, TypeError, KeyError):
            pass

if full is not None:
    with render_inputs(full):
        render_original(route, label, route in RESEARCH_ROUTES)
else:
    st.title(label)
    st.caption(study)
    render_report(label)
    options = {}
    for key, scope in evidence_scopes(label).items():
        payload = approved_payload(key, os.environ)
        if payload is not None:
            options[key] = (scope, payload)
    if options:
        selected = next(iter(options))
        if len(options) > 1:
            selected = st.selectbox("Approved analytical evidence", tuple(options),
                                    format_func=lambda key: options[key][0]["label"],
                                    key=f"approved_evidence_{route}")
        scope, payload = options[selected]
        st.caption(f"Published scope · {scope['label']}. Only approved evidence is available here.")
        with render_inputs(payload, selection=scope["selection"]):
            render_section(route, scope)
    elif cfs is not None:
        st.caption("The archived warehouse and retail source summaries await their own publication clearance.")
    else:
        st.info(PUBLIC_HOLD, icon=":material/lock:")

if cfs is not None:
    render_coverage(*cfs)
