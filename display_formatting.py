"""Display-only number formatting. Never round data used for CSV downloads."""
import math

import pandas as pd


def compact_units(value):
    if pd.isna(value):
        return "—"
    value = float(value)
    if not math.isfinite(value):
        return "—"
    for scale, suffix in [(1e9, "B"), (1e6, "M"), (1e3, "K")]:
        if abs(value) >= scale:
            return f"{value / scale:,.2f}{suffix}"
    return f"{value:,.2f}"


def readable_table(frame):
    """Style numeric demand/error magnitudes and CV, retaining original frame values."""
    formatters = {}
    demand_columns = {"Actual", "Prediction", "Demand", "MAE", "RMSE", "Forecast",
                      "Predicted_Demand", "Historical_P90", "Observed_Sum", "Mean_Weekly_Demand",
                      "Weekly_Std_Dev", "Min_Weekly_Demand", "Max_Weekly_Demand", "Mean_Weekly_Demand",
                      "Projected_Total_Demand", "Average_Weekly_Demand", "Peak_Weekly_Demand",
                      "Recent_4Week_Mean_Observed", "Absolute_Error", "Mean_MAE", "Mean_RMSE",
                      "Actual_Month_Total", "Predicted_Month_Total", "Month_Total_Error", "Average_Width", "Total_Width",
                      "Average Interval Width", "Point Forecast MAE", "Total_Demand", "Total_Signed_Error", "Mean_Signed_Error",
                      "Cumulative_Projected_Demand", "Underforecast_Units", "Overforecast_Units",
                      "Total_Planning_Loss_Units", "Total_Expected_Loss", "Average_Planned_Capacity"}
    for column in frame.select_dtypes(include="number"):
        if column in demand_columns:
            formatters[column] = compact_units
        elif column == "CV":
            formatters[column] = lambda value: "—" if pd.isna(value) else f"{value:.1%}"
        elif column == "WAPE (%)":
            formatters[column] = lambda value: "—" if pd.isna(value) else f"{value:.2f}%"
        elif column.endswith("_Pct") or column.endswith(" (%)"):
            formatters[column] = lambda value: "—" if pd.isna(value) else f"{value:.2f}%"
    return frame.style.format(formatters, na_rep="—")
