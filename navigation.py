"""Grouped native-widget navigation. One route state; styling never drives routing."""
from dataclasses import dataclass

import streamlit as st


@dataclass(frozen=True)
class Destination:
    route: str
    label: str
    icon: str
    group: str


RESEARCH_OVERVIEW = "Research Overview"
FORECAST_HORIZONS = "Forecast Horizons"
NUMERICAL_STABILITY = "Numerical Stability"
MODEL_STRATEGIES = "Model Strategies"
RESEARCH_VALIDATION = "Research Validation"
WAREHOUSE_HOME = "Executive Overview"
RESEARCH_DESTINATIONS = (
    Destination(RESEARCH_OVERVIEW, "Research Overview", "science", "FINAL RESEARCH"),
    Destination(FORECAST_HORIZONS, "Forecast Horizons", "timeline", "FINAL RESEARCH"),
    Destination(NUMERICAL_STABILITY, "Numerical Stability", "tune", "FINAL RESEARCH"),
    Destination(MODEL_STRATEGIES, "Model Strategies", "account_tree", "FINAL RESEARCH"),
    Destination(RESEARCH_VALIDATION, "Research Validation", "fact_check", "FINAL RESEARCH"),
)
WAREHOUSE_DESTINATIONS = (
    Destination("Executive Overview", "Overview", "dashboard", "WORKSPACE"),
    Destination("Historical Demand", "Demand Trends", "show_chart", "ANALYTICS"),
    Destination("Warehouse Analytics", "Warehouse Explorer", "warehouse", "ANALYTICS"),
    Destination("Model Comparison", "Model Performance", "bar_chart", "ANALYTICS"),
    Destination("Future Forecasting", "Demand Outlook", "trending_up", "FORECAST & PLANNING"),
    Destination("Operational Insights", "Planning Insights", "assignment", "FORECAST & PLANNING"),
    Destination("Model Validation", "Forecast Reliability", "verified_user", "RESEARCH"),
    Destination("Data Foundation", "Data Foundation", "database", "RESEARCH"),
)
DESTINATIONS = (*RESEARCH_DESTINATIONS, *WAREHOUSE_DESTINATIONS)
ROUTES = [item.route for item in DESTINATIONS]
RESEARCH_ROUTES = [item.route for item in RESEARCH_DESTINATIONS]
WAREHOUSE_ROUTES = [item.route for item in WAREHOUSE_DESTINATIONS]
LABELS = {item.route: item.label for item in DESTINATIONS}

# Only public, authored st-key container classes are used for menu styling.
# Sidebar sizing uses its accessible region name; routing is entirely native.
CSS = """<style>
[aria-label="Sidebar"]:has(.st-key-wiq_navigation) {width:252px!important;min-width:252px!important;max-width:252px!important;background:#fbfcfe!important;}
.st-key-wiq_navigation {padding:0 0 12px;margin-top:-24px;}
.st-key-wiq_brand {min-height:69px;}
.st-key-wiq_navigation [class*="st-key-wiq_group_"] {min-height:39px;}
.st-key-wiq_navigation {gap:4px!important;}
.wiq-brand {display:flex;gap:11px;align-items:center;padding:0 3px 25px;}
.wiq-logo {display:grid;place-items:center;width:35px;height:39px;background:#182e4c;border-radius:10px;color:#fff;flex-shrink:0;}
.wiq-brand strong {font-size:19px;letter-spacing:-.045em;font-weight:750;line-height:1.3;color:#182e4c;}
.wiq-brand small {display:block;font-size:11px;color:#617087;line-height:1.6;letter-spacing:.01em;}
.wiq-section {padding:17px 10px 7px;font-size:10px;font-weight:700;letter-spacing:.11em;color:#68768a;line-height:1.5;}
.st-key-wiq_navigation button {width:100%;justify-content:flex-start!important;text-align:left!important;min-height:43px!important;padding:10px 12px!important;border:0!important;border-left:3px solid transparent!important;border-radius:7px!important;background:transparent!important;color:#4d5d73!important;box-shadow:none!important;transition:background .12s ease,color .12s ease;}
.st-key-wiq_navigation button p {font-size:13px!important;font-weight:550!important;letter-spacing:-.01em;white-space:nowrap;}
.st-key-wiq_navigation button>div {justify-content:flex-start!important;width:100%;}
.st-key-wiq_navigation button:hover {background:#edf1f6!important;color:#192f4b!important;}
.st-key-wiq_active button {background:#e8f0fa!important;color:#215cab!important;border-left-color:#2866c9!important;}
.st-key-wiq_active button p {font-weight:700!important;}
.st-key-wiq_navigation button:focus-visible {outline:3px solid #2866c9!important;outline-offset:2px!important;}
.wiq-study {display:flex;align-items:center;gap:7px;margin:30px 8px 0;padding:11px 0;color:#536278;font-size:10px;font-weight:600;white-space:nowrap;}
.wiq-study svg {flex-shrink:0;color:#6a7b91;}
.wiq-current {font-size:10px;color:#536278;margin:0 8px;line-height:1.5;}
.st-key-wiq_navigation .wiq-current {font-size:10px!important;}
@media(prefers-reduced-motion:reduce){.st-key-wiq_navigation button{transition:none;}}
@media(max-width:640px){[aria-label="Sidebar"]:has(.st-key-wiq_navigation){width:252px!important;min-width:252px!important;max-width:85vw!important;}}
</style>"""


def navigate(route):
    """Shared callback for the sidebar and Overview shortcuts."""
    if route not in ROUTES:
        raise ValueError(f"Unknown dashboard route: {route}")
    if route in WAREHOUSE_ROUTES:
        st.session_state["last_warehouse_route"] = route
    else:
        st.session_state["last_research_route"] = route
    st.session_state["navigation"] = route


def _render_destination(item, index, current):
    active = item.route == current
    with st.container(key="wiq_active" if active else f"wiq_item_{index}"):
        st.button(item.label, icon=f":material/{item.icon}:", key="nav_" + item.route,
                  type="tertiary", width="stretch", on_click=navigate, args=(item.route,))


def render_navigation():
    if st.session_state.get("navigation") not in ROUTES:
        st.session_state["navigation"] = RESEARCH_OVERVIEW
    current = st.session_state["navigation"]
    st.markdown(CSS, unsafe_allow_html=True)
    with st.sidebar, st.container(key="wiq_navigation"):
        with st.container(key="wiq_brand"):
            st.markdown('''<div class="wiq-brand"><span class="wiq-logo" aria-hidden="true"><svg width="23" height="23" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"><path d="M3 20V8l9-5 9 5v12H3Z"/><path d="M7 20v-9h10v9M7 14h10M7 17h10"/></svg></span><div><strong>Warehouse IQ</strong><small>Demand Intelligence</small></div></div>''', unsafe_allow_html=True)
        st.markdown('<div class="wiq-section" role="heading" aria-level="2">FINAL RESEARCH</div>', unsafe_allow_html=True)
        if current in RESEARCH_ROUTES:
            for index, item in enumerate(RESEARCH_DESTINATIONS):
                _render_destination(item, index, current)
        else:
            last_route = st.session_state.get("last_research_route")
            st.button("Final Research", icon=":material/science:", key="nav_research_track",
                      type="tertiary", width="stretch", on_click=navigate,
                      args=(last_route if last_route in RESEARCH_ROUTES else RESEARCH_OVERVIEW,))
        st.markdown('<div class="wiq-section" role="heading" aria-level="2">ORIGINAL WAREHOUSE OPERATIONS</div>', unsafe_allow_html=True)
        if current in RESEARCH_ROUTES:
            last_route = st.session_state.get("last_warehouse_route")
            st.button("Warehouse Operations", icon=":material/warehouse:", key="nav_warehouse_track",
                      type="tertiary", width="stretch", on_click=navigate,
                      args=(last_route if last_route in WAREHOUSE_ROUTES else WAREHOUSE_HOME,))
            st.markdown('<div class="wiq-study">Final study · M5 and Favorita</div>', unsafe_allow_html=True)
            st.markdown(f'<p class="wiq-current">Current page: {LABELS[current]}<br>Retrospective evaluation</p>', unsafe_allow_html=True)
            return current

        previous_group = None
        for index, item in enumerate(WAREHOUSE_DESTINATIONS, start=len(RESEARCH_DESTINATIONS)):
            if item.group != previous_group:
                with st.container(key=f"wiq_group_{index}"):
                    st.markdown(f'<div class="wiq-section" role="heading" aria-level="2">{item.group}</div>', unsafe_allow_html=True)
                previous_group = item.group
            _render_destination(item, index, current)
        st.markdown('''<div class="wiq-study"><svg aria-hidden="true" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="4" y="5" width="16" height="16" rx="2"/><path d="M8 3v4m8-4v4M4 10h16"/></svg>Historical Study · 2014–2016</div>''', unsafe_allow_html=True)
        # Native text makes the selected route explicit to assistive technology.
        st.markdown(f'<p class="wiq-current">Current page: {LABELS[current]}<br>Archived research · No live monitoring</p>', unsafe_allow_html=True)
    return current
