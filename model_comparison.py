"""Interactive comparison page; rankings never cross evaluation boundaries."""
from ui_controls import choice
from product_layout import insights, chips, panel
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from chart_access import chart_header, chart_options, chart_view, data_section, filters, download_frame, source_detail
from product_layout import PLOT_CONFIG

from comparison_data import (FILES, GROUPS, available_metrics, load_comparison,
                             rank_models, reconciliation_predictions, table)
from data_loading import DataIssue, inventory, read_csv, source_directory
from display_formatting import compact_units, readable_table
from overview import COLORS, data_download
from design_system import style_plot, finding


def comparison_chart(figure, key, height=400):
    """Consistent BI chart surface shared by six specialty pages."""
    chart_header(key)
    st.plotly_chart(style_plot(figure, height), width="stretch", key=key,
                    config=PLOT_CONFIG)


def prediction_panel(predictions, selected, key, label):
    frame = predictions.loc[predictions.Model.isin(selected)].copy()
    unavailable = sorted(set(selected) - set(predictions.Model))
    if unavailable:
        st.info("Aligned predictions are not exported for: " + ", ".join(unavailable) + ". Their summary scores remain available.")
    if frame.empty:
        st.info("No aligned prediction series for the selected models.")
        return
    if frame.Entity.nunique() != 1:
        raise DataIssue("Select one prediction entity before drawing actual vs predicted demand.")
    actual = frame[["Date", "Actual"]].drop_duplicates().sort_values("Date")
    figure = go.Figure()
    figure.add_trace(go.Scatter(x=actual.Date, y=actual.Actual, name="Actual demand", mode="lines+markers",
                               line=dict(color="#172b4d", width=2.5), marker=dict(size=4)))
    for model, model_rows in frame.groupby("Model", sort=False):
        rows = model_rows.sort_values("Date")
        figure.add_trace(go.Scatter(x=rows.Date, y=rows.Prediction, name=f"Predicted · {model}", mode="lines",
                                   line=dict(color=COLORS.get(model), width=2, dash="dash")))
    figure.update_layout(hovermode="x unified", yaxis_title="Weekly order demand (units)", xaxis_title="Recorded weekly date")
    figure.update_traces(hovertemplate="%{y:,.0f} units<extra>%{fullData.name}</extra>")
    comparison_chart(figure, key, height=440)
    st.caption(label + " Actuals are counted once per date. Lines are saved weekly predictions, not newly generated forecasts.")
    data_download(frame, f"{key}_aligned_predictions")


def supplementary_panel(directory):
    with data_section("Supplementary exports · unverified evaluation metadata · no rankings", 'Full Data Tables'):
        records = [r for r in inventory(directory) if r["type"] == ".csv" and
                   (r["evaluation_context"]["family"].startswith("Supplementary") or
                    r["evaluation_context"]["family"] == "External M5 validation")]
        st.caption("These exports lack verified exact evaluation dates or use an external dataset. They are excluded from primary-data rankings. Original rows are displayed without model ranks; similar scores do not establish compatible tasks.")
        if not records:
            st.info("No supplementary CSV metadata available.")
            return
        selected = st.selectbox("Supplementary CSV", [r["file"] for r in records], key="comparison_supplementary", persist_state="session")
        record = next(r for r in records if r["file"] == selected)
        context = record["evaluation_context"]
        st.warning(f"Evaluation metadata: UNVERIFIED · {context['period']}")
        source_detail(f"Source: {selected} · {context['caution']}")
        frame = read_csv(directory, selected)
        st.dataframe(readable_table(frame), width="stretch", hide_index=True)
        download_frame(frame,"supplementary",key="comparison_supplementary_download",label="Download supplementary CSV",filename=selected.split("/")[-1])


def render_model_comparison():
    directory = source_directory()
    overview_slot = st.container()
    with st.container(key="wiq_toolbar_comparison"):
        group = st.selectbox("Evaluation group", GROUPS, key="comparison_group", persist_state="session")
    refine_box = chart_options('comparison_ranked')
    plot_slot = st.container()
    insight_slot = st.container()
    details_slot = st.container()
    kwargs = {}
    try:
        with refine_box:
            if group == GROUPS[1]:
                kwargs["fold"] = st.selectbox("Retrospective cohort", ["Pooled 2014–2015", "2014", "2015"], key="comparison_fold", persist_state="session")
            elif group == GROUPS[2]:
                warehouses = table(directory, "warehouse", ["Warehouse"]).Warehouse.dropna().unique()
                kwargs["warehouse"] = st.selectbox("Comparison warehouse", sorted(warehouses), key="comparison_warehouse", persist_state="session")
            elif group == GROUPS[3]:
                horizons = table(directory, "recursive_summary", ["Horizon_Weeks"]).Horizon_Weeks.unique().tolist()
                kwargs["horizon"] = st.selectbox("Recursive horizon (weeks)", sorted(horizons), index=len(horizons) - 1, key="comparison_horizon", persist_state="session")
                warehouses = table(directory, "recursive_predictions", ["Warehouse"]).Warehouse.dropna().unique()
                kwargs["recursive_scope"] = st.selectbox("Recursive evaluation sample", ["Pooled eligible warehouses"] + sorted(warehouses), key="comparison_recursive_scope", persist_state="session")
        comparison = load_comparison(directory, group, **kwargs)
        scores, predictions, meta = comparison.scores, comparison.predictions, comparison.metadata
        with details_slot:
            st.caption(f"SELECTED EVALUATION · {meta['Evaluation_Period']} · {meta['Horizon']} · {meta['Target']}")
            with st.container():
                with data_section("Evaluation method and data sources", 'Methodology'):
                    a, b = st.columns(2)
                    with a:
                        st.markdown("**Evaluation period**")
                        st.write(meta["Evaluation_Period"])
                        st.caption(meta["Sample"])
                        st.markdown("**Forecast horizon**")
                        st.write(meta["Horizon"])
                    with b:
                        st.markdown("**Target & methodology**")
                        st.write(meta["Target"])
                        st.caption(meta["Methodology"])
                        if meta.get("Forecast_Origin"):
                            st.caption("Forecast origin: " + meta["Forecast_Origin"])
                    source_detail("Metric source: " + meta["Source"])
                    source_detail("Prediction source: " + meta["Prediction_Source"])
        with plot_slot:
            from foundation_data import clarify_2017
            st.warning(clarify_2017(comparison.limitation))
        model_options = sorted(scores.Model.unique()) if not scores.empty else sorted(predictions.Model.unique())
        with refine_box:
            selected = st.multiselect("Models in comparison", model_options, default=model_options, key=f"comparison_models_{group}", persist_state="session")
        if not selected:
            st.info("Select at least one model to compare.")
            return
        metrics = available_metrics(scores)
        if metrics:
            with refine_box:
                metric = choice("Ranking metric", metrics, horizontal=True, key=f"comparison_metric_{group}", persist_state="session")
            ranked = rank_models(scores, metric, selected)
            winners = ranked.loc[ranked.Rank.eq(1)]
            with overview_slot:
                st.subheader("Performance within the selected cohort")
                a, b, c = st.columns(3)
                a.metric("Lowest selected " + metric, f"{ranked[metric].min():.2f}%" if metric == "WAPE (%)" else compact_units(ranked[metric].min()))
                b.metric("Selected models", len(ranked))
                c.metric("Comparable evaluation cohorts", 1)
                unit = "percent" if metric == "WAPE (%)" else "order-demand units"
                finding(f"Lowest {metric} in the selected cohort: {', '.join(winners.Model)}",
                        f"Within this compatible evaluation group only. Lower is better; this descriptive result does not establish statistical superiority.")
            plot_frame = ranked.assign(Display_Value=[f"{v:.2f}%" if metric == "WAPE (%)" else compact_units(v) for v in ranked[metric]])
            figure = px.bar(plot_frame, x=metric, y="Model", orientation="h", color="Model", color_discrete_map=COLORS, text="Display_Value")
            figure.update_yaxes(autorange="reversed", title=None, categoryorder="array", categoryarray=ranked.Model.tolist())
            figure.update_traces(textposition="outside", cliponaxis=False,
                                 hovertemplate="%{y}<br>%{x:,.4f}<extra></extra>")
            figure.update_layout(showlegend=False, xaxis_title=f"{metric} · {unit}")
            for trace in figure.data:
                trace.marker.color = "#087f8c" if trace.name in winners.Model.tolist() else "#7b8da4"
            with plot_slot, panel("model_ranking", "Model ranking · comparable cohort only", f"{group} · {metric} · lower is better"):
                comparison_chart(figure, "comparison_ranked", height=max(300, 36 * len(ranked)))
            with insight_slot:
                insights([
                    ("Key finding", ', '.join(winners.Model), f"Lowest selected {metric} in this cohort; exact ties are retained."),
                    ("Important caveat", "Comparable cohort only", "Period, target, horizon and methodology stay together. No cross-cohort leaderboard."),
                    ("Explore next", "Check aligned predictions", "Missing trajectories are disclosed; summary scores do not create missing observations."),
                ])
            table_columns = ["Rank", "Model", "Model_Type"] + metrics + ["Evaluation_Period", "Horizon", "Target", "Methodology", "Sample", "Source"]
            with data_section("Explore complete ranked results & evaluation metadata", 'Full Data Tables'):
                st.dataframe(readable_table(ranked[table_columns]), width="stretch", hide_index=True)
            st.caption("Ranks are recalculated within the selected models; exact ties share a rank. WAPE is an error measure, not an accuracy percentage. MAE and RMSE use demand units. CSV downloads retain numerical precision.")
            download_frame(ranked,"model_comparison",key="comparison_download",label="Download ranked comparison",filename="model_comparison.csv")
        else:
            st.info("Per-warehouse 4/8-week summary scores are not exported. No missing metrics or rankings are manufactured; aligned predictions can still be viewed below. Select the pooled sample or 12 weeks for exported scores.")
            st.caption("Model types: Recursive XGBoost · recursive gradient-boosted trees; Seasonal Naive · seasonal benchmark.")
        predictions_tab, extras_tab = st.tabs(["Aligned predictions", "Supplementary evidence"])
        if not predictions.empty:
            with predictions_tab:
                st.subheader("Actual vs predicted · aligned historical observations")
                viewed = predictions
                subset_note = ""
                if group == GROUPS[1] and kwargs["fold"] == "Pooled 2014–2015":
                    year = st.selectbox("Prediction fold to view", sorted(predictions.Date.dt.year.unique()), key="comparison_prediction_year", persist_state="session")
                    viewed = predictions.loc[predictions.Date.dt.year.eq(year)]
                    subset_note = f"Chart shows the {year} fold only; rankings above use the pooled 2014–2015 errors. "
                elif predictions.Entity.nunique() > 1:
                    entity = st.selectbox("Prediction warehouse to view", sorted(predictions.Entity.unique()), key="comparison_prediction_warehouse", persist_state="session")
                    viewed = predictions.loc[predictions.Entity.eq(entity)]
                    subset_note = f"Chart shows {entity} only; rankings above use the selected pooled sample. "
                source_detail("Source: " + meta["Prediction_Source"])
                prediction_panel(viewed, selected, "comparison_actual_predicted", subset_note + f"{viewed.Date.min():%d %b %Y} – {viewed.Date.max():%d %b %Y} · {viewed.Entity.iloc[0]}.")
        elif group == GROUPS[2]:
            with predictions_tab:
                st.info("Complete aligned CSV predictions matching these rolling scores are unavailable. The 51-week reconciliation export is a separate diagnostic and is not used to illustrate or recompute these rankings.")
                if st.checkbox("Show separate 51-week reconciliation prediction diagnostic", key="comparison_reconciliation", persist_state="session"):
                    diagnostic = reconciliation_predictions(directory, kwargs["warehouse"])
                    st.subheader("Separate diagnostic · original vs reconciled predictions")
                    source_detail(f"Source: {FILES['reconciliation']} · {diagnostic.Date.min():%d %b %Y} – {diagnostic.Date.max():%d %b %Y} · 51-week common-period subset · no per-warehouse summary rankings")
                    st.caption("Model types: original nonnegative XGBoost warehouse forecast and hierarchical reconciliation of that forecast. This chart is independent of the selected rolling-model filters above.")
                    prediction_panel(diagnostic, list(diagnostic.Model.unique()), "comparison_reconciliation_plot", "Different sample and methodology from the rolling score table above.")
        st.divider()
        with extras_tab:
            supplementary_panel(directory)
        st.caption("Order demand is not verified shipment volume. No causal explanation for demand spikes is inferred. No model has been retrained and no forecast has been generated.")
    except (DataIssue, OSError, ValueError, KeyError) as exc:
        st.warning(f"Model comparison data unavailable: {exc}")
