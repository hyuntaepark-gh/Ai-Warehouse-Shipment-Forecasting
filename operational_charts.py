"""Presentation transformations of validated archived records; no new risk categories."""
from html import escape

import plotly.graph_objects as go

from bi_components import BLUE, INK

HEAT_COLORS = [(240,245,252), (168,201,241), (33,87,162)]


def heatmap_text_color(percent):
    """Choose black/white for contrast against the quantitative color interpolation."""
    scale = max(0, min(float(percent) / 100, 1)) * 2
    index = min(int(scale), 1)
    weight = scale - index
    rgb = [(a + (b-a)*weight) / 255 for a,b in zip(HEAT_COLORS[index], HEAT_COLORS[index+1])]
    linear = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in rgb]
    luminance = sum(v*w for v,w in zip(linear,[.2126,.7152,.0722]))
    return "#ffffff" if luminance < .179 else "#000000"


def warehouse_name(name):
    return "Warehouse " + name.removeprefix("Whse_")


def comparison_markup(summary):
    rows = ['<div class="ops-compare-head"><span>Warehouse</span><span>Peak / P90</span><span>Ratio</span><span>Source label</span></div>']
    # Sort a descriptive demand/reference ratio, never a model accuracy or invented risk score.
    for row in summary.sort_values("Max_Demand_to_P90_Ratio",ascending=False,kind="stable").itertuples():
        pct = row.Max_Demand_to_P90_Ratio * 100
        rows.append(f'<div class="ops-compare-row" aria-label="{escape(row.Warehouse)}: {pct:.1f}% of historical P90; source label {escape(row.Illustrative_Risk_Level)}"><span class="ops-wh">{escape(warehouse_name(row.Warehouse))}</span><div class="ops-track"><span style="width:{min(pct,100):.8f}%"></span></div><span class="ops-ratio">{pct:.1f}%</span><span class="ops-label">{escape(row.Illustrative_Risk_Level)}</span></div>')
    rows.append('<p class="ops-scale">Full track = historical P90. Labels are copied, not derived from the bar.</p>')
    return "".join(rows)


def weekly_heatmap(weekly):
    pivot = weekly.pivot(index="Warehouse",columns="Week",values="Demand_to_P90_Ratio").sort_index().sort_index(axis=1)
    dates = list(pivot.columns)
    percents = pivot * 100
    # Custom hover retains full source precision and the separate source category.
    lookup = weekly.set_index(["Warehouse","Week"])
    custom = [[[float(lookup.loc[(w,d),"Predicted_Demand"]),float(lookup.loc[(w,d),"Historical_P90"]),
                str(lookup.loc[(w,d),"Illustrative_Risk_Level"])] for d in dates] for w in pivot.index]
    figure = go.Figure(go.Heatmap(x=dates,y=list(pivot.index),z=percents.to_numpy(),customdata=custom,
        zmin=0,zmax=100,xgap=4,ygap=5, colorscale=[[0,"#f0f5fc"],[.5,"#a8c9f1"],[1,"#2157a2"]],
        colorbar=dict(orientation="h",y=-.3,x=.5,xanchor="center",len=.65,thickness=8,
                      tickvals=[0,50,100],ticktext=["0%","50%","100% of P90"],tickfont_size=11),
        hovertemplate="%{y} · %{x|%d %b %Y}<br>Projected / P90: %{z:.4f}%<br>Projected demand: %{customdata[0]:,.4f}<br>Historical P90: %{customdata[1]:,.4f}<br>Source weekly label: %{customdata[2]}<extra></extra>"))
    for warehouse in pivot.index:
        for date in dates:
            value = percents.loc[warehouse,date]
            figure.add_annotation(x=date,y=warehouse,text=f"{value:.0f}%",showarrow=False,
                                  font=dict(size=12,color=heatmap_text_color(value)))
    figure.update_xaxes(tickvals=dates[::2] if len(dates)>6 else dates,tickformat="%d %b",side="top",title_text="")
    figure.update_yaxes(autorange="reversed",tickvals=list(pivot.index),ticktext=["Whse " + w[-1] for w in pivot.index],title_text="",showgrid=False)
    return figure, pivot


def detail_figure(records):
    figure = go.Figure()
    figure.add_trace(go.Scatter(x=records.Week,y=records.Predicted_Demand,name="Archived projection",mode="lines+markers",
        line=dict(color=BLUE,width=3),marker_size=6,fill="tozeroy",fillcolor="rgba(40,102,201,.08)",
        hovertemplate="%{x|%d %b %Y}<br>Projected demand: %{y:,.4f} units<extra></extra>"))
    figure.add_trace(go.Scatter(x=records.Week,y=records.Historical_P90,name="Historical P90 reference",mode="lines",
        line=dict(color=INK,width=2,dash="dot"),hovertemplate="Historical P90: %{y:,.4f} units<extra></extra>"))
    figure.update_yaxes(title_text="Demand units",tickformat=".3s",rangemode="tozero")
    figure.update_xaxes(tickformat="%d %b",title_text="Archived projected week")
    figure.update_layout(hovermode="x unified")
    return figure
