"""Historical Demand Analysis page; all charts represent exported actual observations."""
from ui_controls import choice
from product_layout import insights, mini_cards, panel
import calendar

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from chart_access import chart_header, chart_options, chart_view, data_section, filters, download_frame, source_detail

from data_loading import DataIssue, source_directory
from historical_data import (LEVELS, SOURCES, aggregate_history, coverage, load_history,
                             seasonal_profile, trend_with_gaps, variability)
from overview import chart, data_download
from display_formatting import compact_units, readable_table
from design_system import finding, MODEL_PALETTE, WAREHOUSE_COLORS

PALETTE = MODEL_PALETTE[:4]


def render_historical():
    overview_slot = st.container()
    with st.columns([1,2])[0]:
        scope = choice("Historical data scope", list(SOURCES), horizontal=True, key="history_scope", persist_state="session")
    with filters('Refine view', 'historical_history_filters'):
        try:
            history = load_history(source_directory(), scope)
        except (DataIssue, OSError, ValueError) as exc:
            st.warning(f"Historical demand data unavailable: {exc}")
            return
        a, b = st.columns(2)
        with a:
            years = st.multiselect("Available years", sorted(history.Year.unique().tolist()),
                                   default=sorted(history.Year.unique().tolist()), key=f"history_years_{scope}", persist_state="session")
        with b:
            level = st.selectbox("Trend aggregation", list(LEVELS), key="history_level", persist_state="session")
        selected = history.loc[history.Year.isin(years)]
        if scope == "Warehouse sample":
            warehouses = st.multiselect("Historical warehouses", sorted(history.Series.unique()),
                                        default=sorted(history.Series.unique()), key="history_warehouses", persist_state="session")
            selected = selected.loc[selected.Series.isin(warehouses)]
    if scope == "Aggregate demand":
        st.caption("Observed weekly actuals only · 2014–2016 aggregate sample · 2016 holdout reference")
    else:
        st.warning("Warehouse history is a 51-week common-period sample: 10 Jan–25 Dec 2016 for each warehouse. It is not a full-year warehouse history. January and Q1 have reduced coverage. This sample is separate from the 52-week aggregate export; no missing warehouse weeks are reconstructed.")
    if selected.empty:
        st.info("Select at least one available year and, for warehouse history, one warehouse.")
        return

    with overview_slot:
        summary = variability(selected)
        a, b, c, d = st.columns(4)
        a.metric("Observed demand sum", compact_units(selected.Demand.sum()))
        a.caption("Recorded units in the selected sample")
        b.metric("Weekly observations", f"{len(selected):,}")
        b.caption("Warehouse-weeks" if scope == "Warehouse sample" else "Distinct weekly actuals")
        c.metric("Selected series", selected.Series.nunique())
        c.caption("Each warehouse remains a separate series" if scope == "Warehouse sample" else "Aggregate order demand")
        d.metric("Observed timestamps", selected.Date.nunique())
        d.caption(f"{selected.Date.min():%d %b %Y} – {selected.Date.max():%d %b %Y}")

        yearly = selected.groupby("Year")["Demand"].sum()
        leading_year = int(yearly.idxmax())
        if len(yearly) > 1:
            finding(f"{leading_year} has the largest recorded total in the current selection",
                    f"{compact_units(yearly.max())} observed order-demand units across its exported weekly sample. Comparisons describe available observed weeks, not annualized warehouse totals or forecast accuracy.")
        else:
            finding(f"{leading_year}: {compact_units(yearly.iloc[0])} recorded units",
                    "This is the selected observed-week sample, not a new forecast or an extrapolated full-year estimate.")

    st.subheader("How did observed weekly demand evolve?")
    grouped = aggregate_history(selected, level)
    figure = px.line(trend_with_gaps(grouped, level), x="Period", y="Demand", color="Series", markers=True,
                     color_discrete_sequence=PALETTE, color_discrete_map={**WAREHOUSE_COLORS, "Aggregate actual demand": "#172b4d"}, custom_data=["Observations", "First_Observation", "Last_Observation"],
                     labels={"Period": "Recorded weekly date" if level == "Weekly" else f"{level} bucket of recorded weekly dates",
                             "Demand": "Actual order demand (units)" if level == "Weekly" else "Sum of observed weekly actuals (units)"})
    figure.update_traces(connectgaps=False, hovertemplate="%{x|%Y-%m-%d}<br>%{y:,.0f} units<br>%{customdata[0]} observed weeks<extra>%{fullData.name}</extra>")
    with panel("demand_trend", "Recorded demand over time", "Missing periods remain gaps; no interpolated values"):
        chart(figure, "history_trend")
    with data_section("Trend interpretation & download", 'Methodology'):
        st.caption(f"{'Actual demand' if level == 'Weekly' else 'Aggregated actual demand'} · {level.lower()} view. Breaks indicate unselected or missing periods; no values are interpolated or zero-filled. Longer buckets contain more weekly observations.")
        st.caption("Monthly and quarterly buckets assign the whole weekly value to its recorded timestamp. They are not exact calendar-month or calendar-quarter transaction totals. Annual bars likewise summarize the exported weekly sample.")
        data_download(grouped, "historical_trend")

    insights([
        ("Key finding", f"{leading_year} leads the selected samples", f"{compact_units(yearly.max())} recorded units; compare alongside observed-week counts."),
        ("Important caveat", "Observed demand only", "No forecasts are scored here. Warehouse history has 51 weeks, not a complete calendar year."),
        ("Explore next", "Separate scale from variability", "Compare periods, then inspect monthly weekly means and the distribution."),
    ])
    trend_tab, period_tab, season_tab, variable_tab = st.tabs(["Trend", "Period comparison", "Seasonality", "Variability"])
    with trend_tab:
        mini_cards([(str(year), compact_units(total), "Sum of selected observed weekly demand") for year, total in yearly.items()])
        st.caption("Annual cards sum exported weekly observations only; no extrapolation or missing weeks.")
    with period_tab:
        st.subheader("How do the recorded periods compare?")
        comparison_level = choice("Comparison period", ["Annual", "Quarterly", "Monthly"], horizontal=True, persist_state="session", key="bi_historical_comparison_period")
        compared = aggregate_history(selected, comparison_level)
        compared["Year_Label"] = compared.Year.astype(str)
        compared["Bucket"] = (compared.Period.dt.year.astype(str) if comparison_level == "Annual" else
                              "Q" + compared.Period.dt.quarter.astype(str) if comparison_level == "Quarterly" else
                              compared.Period.dt.month.map(lambda m: calendar.month_abbr[m]))
        color = "Year_Label" if scope == "Aggregate demand" else "Series"
        orders = {"Bucket": list(calendar.month_abbr)[1:]} if comparison_level == "Monthly" else {}
        figure = px.bar(compared, x="Bucket", y="Demand", color=color, barmode="group",
                        color_discrete_sequence=PALETTE, color_discrete_map=WAREHOUSE_COLORS, category_orders=orders,
                        custom_data=["Observations", "Series", "Year_Label"],
                        labels={"Demand": "Observed weekly actuals summed (units)", "Bucket": comparison_level, "Year_Label": "Year"})
        figure.update_traces(hovertemplate="%{x}<br>%{y:,.0f} units<br>%{customdata[0]} observed weeks<br>%{customdata[1]} · %{customdata[2]}<extra></extra>")
        chart(figure, "history_comparisons")
        st.caption("Aggregated historical actuals, not predictions. Compare totals alongside observed-week counts. Warehouse annual totals describe only the 51-week sample; they must not be treated as full-year totals.")
        data_download(compared, "historical_period_comparisons")

    with season_tab:
        st.subheader("When was demand higher or more variable?")
        season = seasonal_profile(selected)
        season["Sample"] = season.Series + " · " + season.Year.astype(str)
        means = season.pivot(index="Sample", columns="Month", values="Mean_Weekly_Demand").reindex(columns=range(1, 13))
        counts = season.pivot(index="Sample", columns="Month", values="Observed_Weeks").reindex(index=means.index, columns=range(1, 13))
        figure = go.Figure(go.Heatmap(z=means.to_numpy(), x=list(calendar.month_abbr)[1:], y=means.index,
                                     customdata=counts.to_numpy(), colorscale="Teal", colorbar=dict(title="Mean units / week"),
                                     hoverongaps=False, hovertemplate="%{y} · %{x}<br>Mean weekly actual: %{z:,.0f} units<br>%{customdata} observed weeks<extra></extra>"))
        chart(figure, "history_seasonality")
        st.caption("Mean weekly actual demand by recorded month and year. Using weekly means reduces the effect of different numbers of weeks per month; hover for counts. Blank cells mean no observations, not zero demand. These are descriptive patterns from a short sample, not proof of recurring seasonality.")
    with variable_tab:
        distribution = selected.assign(Sample=selected.Series + " · " + selected.Year.astype(str))
        figure = px.box(distribution, x="Sample", y="Demand", color="Series", points="all",
                        color_discrete_sequence=PALETTE, color_discrete_map={**WAREHOUSE_COLORS, "Aggregate actual demand": "#172b4d"}, hover_data=["Date", "Evaluation"],
                        labels={"Demand": "Weekly actual order demand (units)", "Sample": "Series / observed year"})
        chart(figure, "history_variability")
        st.caption("Each point is an observed weekly actual; boxes describe its distribution. Spikes show variation in recorded demand, not forecast errors. Different warehouses have different scales.")
        with data_section("Explore variability statistics by series and year", 'Full Data Tables'):
            st.dataframe(readable_table(summary), width="stretch", hide_index=True)
        st.caption("Weekly standard deviation uses the sample formula (n−1). CV = standard deviation / mean weekly demand; it is undefined for a nonpositive mean or fewer than two observations. CV is descriptive variability, not a forecast performance metric.")
        if summary.CV.notna().any():
            most_variable = summary.loc[summary.CV.idxmax()]
            st.write(f"Within the selected samples, **{most_variable.Series} · {int(most_variable.Year)}** has the highest relative weekly variability (CV **{most_variable.CV:.1%}**). This describes observed demand only.")
        data_download(season, "historical_monthly_weekly_means")
        data_download(summary, "historical_variability")

    with data_section("Coverage, sources & missing information", 'Data Sources'):
        source_detail(f"Source: {SOURCES[scope]} · uses {'Actual' if scope == 'Aggregate demand' else 'Demand'} only.")
        if scope == "Aggregate demand":
            st.info("Actual demand is available for 2014–2016. Each weekly actual is counted once despite appearing in multiple model rows. 2014–2015 were retrospective evaluation years; 2016 was the holdout reference. This page describes observed demand, not forecast accuracy.")
        st.dataframe(coverage(selected), width="stretch", hide_index=True)
        st.caption("Gap counts cover only intervals between the first and last exported timestamps. They cannot establish completeness outside that span.")
        st.markdown("""- Aggregate actuals: `timesfm_historical_weekly_predictions.csv`, `Actual` column; model predictions are excluded.
- Warehouse actuals: `hierarchical_warehouse_forecasts.csv`, `Demand` column; XGBoost and reconciled forecasts are excluded.
- Other warehouse exports contain shorter recursive or multi-horizon samples. They are not stitched into this history.
- The original raw daily/transaction dataset and full 2012–2013 history are unavailable in these exports. Exact daily calendar-month totals, product/category history, and a complete multi-year warehouse history cannot be reconstructed.
- Recorded demand represents order demand, not confirmed shipments, inventory, physical capacity, or staffing requirements.
- 2014–2015 retrospective and 2016 holdout labels describe the origin of the exported observations. No error metrics or model rankings are computed on this page.""")
    source_detail(f"Source: {SOURCES[scope]} · all charts show actual or aggregated actual demand · original files remain read-only")

