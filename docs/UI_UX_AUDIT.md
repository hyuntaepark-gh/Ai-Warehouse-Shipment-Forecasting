# Seven-page UI/UX audit — Phase 3

Recorded October 16, 2026 **before interface changes**. Evidence: reviewed all seven
renderers, app shell, theme and shared chart/format helpers; rendered each default
page with Streamlit AppTest against actual exports. All seven rendered without
exceptions. Baseline Overview screenshot: `overview_before.png` in the task's
visualization output directory. Baseline browser viewport: 1103 × 720 screenshot.

## Cross-page findings

- **Hierarchy:** breadcrumb, generic page description, technical all-caps caption,
  info/warning banner, filter controls and then analysis compete for attention.
  Repeated disclaimers often obscure the finding they qualify. Material caveats
  must remain visible; implementation descriptions can move behind disclosure.
- **Typography/spacing:** Streamlit defaults mixed with Arial 13 Plotly text;
  h3/h4 section levels and long captions vary. Cards use 20px padding but their
  context sits outside the card. Long metric labels truncate at narrower widths.
  The shell reserves 4.5rem above content, reducing useful first-screen space.
- **Charts:** shared helpers disagree on margins, heights (330–520+px), legends,
  hover style and range sliders. Overview uses a range slider absent elsewhere.
  Eight-model comparison in a one-third-width column crowds labels. Too many
  categorical model colors imply meaning where neutral context would suffice.
- **Density/duplication:** charts, raw tables, a second copy of tables inside
  download expanders and source/implementation notes repeat. The Overview eagerly
  renders all tabs, including content covered in detail on specialist pages.
- **Responsive/accessibility:** four-column metrics and uneven 2:1 chart rows
  narrow awkwardly; long labels and inline technical field names impede scanning.
  Default muted captions need contrast checks. Color must not be the only cue.
  A small-screen screenshot was available from prior QA; new responsive review
  should check both the available desktop viewport and narrower layouts.
- **Data communication:** WAPE needs a plain-language error definition, never
  “accuracy = 100 − WAPE.” MAE/RMSE are demand quantities. P90 is not capacity or
  an uncertainty bound. Weekly timestamp calendar groups are not exact transaction
  totals. No causal explanation for spikes is supported by these exports.

## Page-by-page findings and recommendations

Counts below include elements in inactive tabs and collapsed expanders, not only
the initially visible view. They describe layout complexity, not performance timings.

| Page | Baseline charts / metrics / captions / tables | Findings | Recommendation |
|---|---|---|---|
| Executive Overview | 9 / 6 / 35 / 11 | No executive thesis; four protocol tabs precede insights; demand chart squeezed beside eight-model ranking; warehouse findings hidden; nine charts duplicate specialist analysis; old PHASE 1 footer; future empty selection displays zero quantity. | **Implement now:** summary, four integrated KPI cards, full-width demand then readable performance chart, warehouse highlights, explicit caveats, deeper-page buttons; retain controls/downloads with supplementary research on demand. Empty archive selection must show unavailable rather than zero. |
| Historical Demand | 4 / 4 / 18 / 6 | Actual-only scope and partial warehouse coverage are sound. Repeated aggregation definitions and equally weighted distribution/seasonality sections lengthen the page. Technical CV needs reader-friendly labeling. | Later: insight-led introduction; trend first; seasonal/variability secondary; preserve visible weekly-calendar and coverage caveats. |
| Model Comparison | 2 / 3 / 15 / 3 | Correct cohort separation, but evaluation metadata fills two columns before chart; a large technical selector and repeated error-measure notes burden newcomers. Chart height grows by model count. | Later: compact cohort identity strip, question-led ranking, readable metric control; methods and model types on demand; retain limitations and unverified metadata warnings. |
| Warehouse Analytics | 6 / 8 / 24 / 11 | Rich filters and valid separate samples; many similar volume/share/CV views and duplicated score tables. Deep dive depends on a metric control in another tab. | Later: warehouse summary first, one comparison chart, visibly scoped deep-dive control; never pool warehouse rankings or annualize 51 weeks. |
| Model Validation | 1 / 0 / 10 / 2 (default view) | Evidence selector appropriately separates seven areas. Technical labels and prose make reliability conclusions harder to locate. Many nested diagnostics, few summary interpretations. | Later: evidence-led reliability summary, concise cohort labels, detail disclosures. Keep ETS selection reuse, unverified dates and interval limitations visible where relevant. |
| Future Forecasting | 2 / 4 / 22 / 11 | Origin and coverage are correct and prominent. Repeated weekly/cumulative/window summaries and numerous expanded table copies increase density. | Later: archive identity, selected horizon summary and one primary chart; keep no-2017-outcomes and no-interval caveats visible; consolidate download tables. |
| Operational Insights | 2 / 3 / 18 / 8 (default view) | Correct preservation of Normal/Watch and no invented severity palette. Long technical captions, raw field-name selectors, repeated summary/reference tables and multiple caveats compete with conditional insights. | Later: plain-language labels, source-linked conditional insights first, method/source detail on demand; retain undocumented risk rules, P90/capacity distinction and illustrative policy limitations. |

## Integrity observations

Existing numerical tests verify cohort separation and source preservation. No new
unsupported result was identified in this review. The current Overview future empty
selection can show zero, conflating no selection with a zero-demand projection;
correct this presentation state during the redesign. Its archive preview should
reuse the complete-coverage checks already used by Future Forecasting. Original
conclusion tables can contain broad source language; keep the dashboard's explicit
research caveats adjacent to their disclosure rather than adopting them as new claims.

The Overview loader currently requires all its bound exports even for headline KPIs.
Optional-source isolation can be considered later; this iteration preserves its
fail-closed behavior. Supplementary source dates cannot be repaired by UI work.

## Scope boundary

Only Executive Overview adopts the proposed design now. The remaining six renderers,
their controls and chart helpers are not restyled until the user reviews this pilot.
No deployment, model execution, data rewriting or source-file modification.
