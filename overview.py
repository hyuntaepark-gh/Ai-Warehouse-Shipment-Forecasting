"""Executive Overview: separate panels for distinct forecasting tasks."""
import pandas as pd
import plotly.express as px
import streamlit as st
from chart_access import chart_header, chart_options, chart_view, data_section, filters, download_frame, source_detail
from product_layout import PLOT_CONFIG

from data_loading import load_manifest
from overview_data import actual_demand
from display_formatting import readable_table

COLORS = {"Actual": "#172b4d", "TimesFM 3.0": "#087f8c", "ETS": "#916128", "Seasonal Naive": "#7855a3",
          "XGBoost": "#087f8c", "Random Forest": "#916128", "Naive": "#7855a3",
          "Recursive XGBoost": "#087f8c"}


def chart(figure, key):
    chart_header(key)
    from design_system import style_plot
    st.plotly_chart(style_plot(figure, 330), width="stretch", key=key,
                    config=PLOT_CONFIG)


def source_note(*names):
    tables = load_manifest()["tables"]
    source_detail("Source: " + " · ".join(tables[name].removeprefix("tables/") for name in names))


def data_download(frame, name):
    download_frame(frame,name)



def demand_plot(weekly, year, models, monthly=False):
    observed = actual_demand(weekly, year).rename(columns={"Actual": "Demand"})
    observed["Series"] = "Actual"
    forecasts = weekly.loc[weekly.Year.eq(year) & weekly.Model.isin(models), ["Date", "Prediction", "Model"]]
    forecasts = forecasts.rename(columns={"Prediction": "Demand", "Model": "Series"})
    plotted = observed.copy() if forecasts.empty else pd.concat([observed, forecasts], ignore_index=True)
    if monthly:
        plotted["Date"] = plotted.Date.dt.to_period("M").dt.to_timestamp()
        plotted = plotted.groupby(["Date", "Series"], as_index=False).Demand.sum()
    figure = px.line(plotted, x="Date", y="Demand", color="Series", color_discrete_map=COLORS,
                     labels={"Demand": "Recorded order demand (units)", "Date": "Weekly timestamp"})
    figure.update_xaxes(rangeslider_visible=True, rangeslider_thickness=0.06)
    figure.update_traces(hovertemplate="%{x|%b %d, %Y}<br>%{y:,.0f} units<extra>%{fullData.name}</extra>")
    return figure, plotted


def render_overview():
    """Use the Overview-only pilot without changing shared specialist-page helpers."""
    from executive_overview import render_overview as render_pilot
    render_pilot()
