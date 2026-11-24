"""Original renderers, lazily dispatched after the public gate."""
from importlib import import_module

PAGES = {
    "Executive Overview": ("executive_overview", "render_overview"),
    "Historical Demand": ("historical", "render_historical"),
    "Warehouse Analytics": ("warehouse", "render_warehouse"),
    "Model Comparison": ("model_comparison", "render_model_comparison"),
    "Future Forecasting": ("future_forecasting", "render_future"),
    "Operational Insights": ("operational_insights", "render_operational"),
    "Model Validation": ("model_validation", "render_validation"),
    "Data Foundation": ("data_foundation", "render_foundation"),
    "Research Overview": ("research_overview", "render_research_overview"),
    "Forecast Horizons": ("forecast_horizons", "render_forecast_horizons"),
    "Numerical Stability": ("numerical_stability", "render_numerical_stability"),
    "Model Strategies": ("model_strategies", "render_model_strategies"),
    "Research Validation": ("research_validation", "render_research_validation"),
}


def render_original(route, title, research):
    from design_system import page_intro
    from product_layout import workspace_header

    module, renderer = PAGES[route]
    workspace_header(title, "Final Research · Retail forecasting" if research
                     else "Original Warehouse Operations · Archived study", include_downloads=False)
    if not research and route not in {"Executive Overview", "Operational Insights", "Data Foundation"}:
        page_intro(route)
    getattr(import_module(module), renderer)()


def render_section(route, scope):
    from chart_access import start_data_center

    start_data_center(scope["label"], include_downloads=False)
    module, default_renderer = PAGES[route]
    getattr(import_module(module), scope.get("renderer", default_renderer))()
