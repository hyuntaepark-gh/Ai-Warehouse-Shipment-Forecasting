"""Result-free context for the independently gated reports."""
import streamlit as st

REPORTS = {
  "Research Overview": [
    "How do forecast horizon and numerical safeguards affect retail forecast error?",
    "The study compares saved M5 and Corporación Favorita results under their reported evaluation cohorts.",
    "The controls help distinguish changes in error from changes in the set of scored origins.",
    "Retail sales evidence describes retrospective evaluations. It does not establish performance on later demand."
  ],
  "Forecast Horizons": [
    "How does forecast error change with the length of the planning window?",
    "The Ridge comparisons match strategies and count the origins that support each horizon.",
    "Longer horizons should be interpreted alongside their scored coverage.",
    "Different horizon windows and overlap limit direct comparisons."
  ],
  "Numerical Stability": [
    "Which preprocessing safeguards matter to the saved Ridge results?",
    "Matched corrections and controlled component ablations are compared within the same retailer, configuration, and horizon.",
    "A matched contrast can guide checks on a forecasting pipeline before model selection.",
    "Unscored and unmatched configurations remain unavailable."
  ],
  "Model Strategies": [
    "How do strategy rankings change across the reported protocols?",
    "Reference models, combination strategies and meta-models are evaluated in separate cohorts.",
    "Eligibility rules determine which strategy comparisons can inform selection.",
    "The results are retrospective. Missing or ineligible estimates do not imply zero error."
  ],
  "Research Validation": [
    "How much statistical and reproducibility evidence supports the comparisons?",
    "The study reports frozen paired contrasts, coverage, bootstrap sensitivity and replay checks.",
    "Verification of artifacts helps distinguish repeatable results from claims that need further testing.",
    "Uncertainty requires independent origins. Artifact replay is separate from independent reproduction."
  ],
  "Overview": [
    "What does the archived study tell us about order demand and forecasting?",
    "The study separates recorded weekly demand, aggregate holdouts, warehouse comparisons and archived projections.",
    "Use comparable errors to prioritize further evaluation and keep network averages separate from individual warehouse evidence.",
    "The exports cover a historical study and do not measure shipment volume or current performance."
  ],
  "Demand Trends": [
    "How do observed order-demand patterns change across periods and warehouse samples?",
    "Weekly actuals are counted once per timestamp within their scope, then grouped by the selected calendar period.",
    "Trend and variability views can help prioritize where to look for changes in demand.",
    "Incomplete and unobserved periods are kept distinct from zero order demand."
  ],
  "Warehouse Explorer": [
    "How do warehouse demand profiles and local evaluation results differ?",
    "The page uses aligned observations, warehouse-scoped rankings and a separate reconciliation diagnostic.",
    "Warehouse-specific patterns can identify where an evaluation needs more attention.",
    "Scores use different coverage and demand scales. The charts do not establish a pooled winner."
  ],
  "Model Performance": [
    "Which model scores can be compared fairly?",
    "The page separates holdout, retrospective, rolling and recursive cohorts. Comparisons use their reported error units and samples.",
    "A ranking can guide model investigation within the selected evaluation cohort.",
    "Untimed supplementary results and separately aligned predictions do not change cohort rankings."
  ],
  "Demand Outlook": [
    "What did the archived forecast project across warehouse planning horizons?",
    "The original fixed-origin projections are grouped by warehouse and summarized across the exported horizons.",
    "The projections and contribution views describe the planning exercise and its assumptions.",
    "These are archived forecasts. Historical backtests do not measure accuracy for their target weeks."
  ],
  "Planning Insights": [
    "Which archived evidence can inform questions about demand pressure?",
    "Forecast-to-reference ratios, historical diagnostics and hypothetical scenarios are treated as distinct evidence.",
    "The views can frame questions for a planner to validate against operating records.",
    "An exported historical reference does not establish physical capacity or current risk."
  ],
  "Forecast Reliability": [
    "What does the available evidence establish about forecast reliability?",
    "Backtests, temporal stability, external validation, uncertainty, diagnostic and recursive checks retain separate evidence scopes.",
    "Review the unit, sample and validation method before acting on an error or a warning flag.",
    "Point accuracy alone does not establish calibrated intervals or independent validation."
  ],
  "Data Foundation": [
    "What source coverage supports the warehouse and retail studies?",
    "The collection distinguishes source summaries from modeled outcomes. The CFS pilot counts published estimate-table records by mode and survey year.",
    "Check source coverage before linking any result to an operational question.",
    "CFS published-record counts and physical shipments, tonnage, transportation value, and warehouse demand are different measures."
  ]
}


def render_report(label):
    question, method, implications, caveats = REPORTS[label]
    st.subheader(question)
    st.write(method)
    st.caption(caveats)
    with st.expander("How to use the evidence"):
        st.write(implications)
