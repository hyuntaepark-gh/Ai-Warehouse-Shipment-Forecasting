# Warehouse Demand Intelligence — design system

The Executive Overview was the initial pilot, and the shared tokens have now been extended to six specialist pages. Philosophy: **insights first, visualizations second,
technical details on demand**. All seven pages now share a navigation shell, typography, chart treatment and question-led introductions.

## Content hierarchy

1. Product identity + Executive Overview title + concise source-derived research finding.
2. Visible historical period and material research caveat.
3. Four high-value KPI cards with value, label and context together.
4. One primary question per chart: historical demand, comparable 2016 errors, local
   warehouse differences. Warehouse and aggregate tasks remain visibly separate.
5. Short evidence-linked insights and navigation to specialist analysis.
6. Existing retrospective, recursive and archived-future controls in supplementary
   research disclosures. Sources, data downloads and detailed methods remain accessible.

No financial savings, operational cause or prospective reliability claim is inferred.
WAPE is error, not accuracy. Monthly sums group weekly timestamps. Archived projections
always carry their December 2016 origin and missing-actuals caveat.

## Visual tokens

| Token | Value | Use |
|---|---|---|
| Ink | #172b4d | Headings, actual-demand line, primary text |
| Secondary text | #526278 | Context and captions; use on white/light background |
| Primary | #087f8c | Interactive accent and selected research result |
| Teal wash | #eaf5f5 | Executive summary and finding emphasis |
| Canvas | #f5f7fb | Existing app background |
| Surface | #ffffff | Cards/charts |
| Rule | #dfe5ef | Subtle separators; avoid boxing every paragraph |
| Context series | #66758c | Comparison bars; no implied risk severity |
| Secondary model | #7855a3 | Seasonal Naive / Naive where legends are required |
| Accessible comparison series | #916128 | Overview ETS / Random Forest; darker than the legacy gold |

Typography: system sans-serif stack shared by HTML and Plotly, no external font
dependency. Body 15–16px, captions 14px, chart labels 14px, section titles 22–24px,
page title 32–38px; KPI values 28–34px. Use sentence case and short labels.
Do not shrink long labels below readable sizes; wrap, stack or allocate space.

Spacing uses an 8px rhythm: 8/16/24/32px. KPI cards have 20px padding, 12px radius
and a light rule. Insight cards use whitespace and a small accent rather than heavy
border/shadow. Buttons use descriptive action labels and retain keyboard focus.

## Charts

- White surfaces, restrained horizontal gridlines, no plot border, clear units.
- Primary demand 400px; eight-model horizontal comparison 420px; supporting charts
  340–380px. Full-width primary charts avoid narrow eight-model rankings.
- No range sliders. Plotly zoom/pan/hover/export remain available.
- Actual demand: navy solid line. Saved predictions: labeled dashed lines, also
  distinguished by legend/text so color is not the only cue.
- Ranking: selected-metric minimum in teal with explicit text; other bars muted.
  Include all exact minimum ties. This is descriptive, not statistical superiority.
- WAPE labels use %, error quantities use K/M/B; hover and CSV preserve precision.
- Default legend below chart, wrapped by Plotly; responsive width, adequate margins.
- No arbitrary risk colors or new severity categories.

## Responsive and accessibility behavior

The original Overview-specific CSS remains in `overview_design.py`; the shared responsive theme and specialist plot helper now live in `design_system.py`.
KPI grid: four columns on wide screens, two on intermediate widths and one on narrow
screens. Insight/navigation grids likewise stack; full-width charts size to their
container. At smaller widths, use reduced horizontal padding and wrapped legends.
Container queries also respond to available content width as the sidebar is resized:
four KPI columns above 1000px, two at 521–1000px and one at 520px or below, with
viewport breakpoints as a fallback.
Controls retain Streamlit accessible labels. All substantive text has readable
contrast; verification computes WCAG contrast for text/background pairs (4.5:1).
Keep native keyboard focus indicators; add clear focus for custom navigation buttons.

Source filenames, metrics definitions, inventory and raw schemas belong in expandable
sections. Evaluation dates, forecast-vs-actual labels and material limitations remain
visible. Display formatting never rounds the underlying DataFrame or download.

## Adoption and checks

The seven-page presentation refresh reuses the same palette and chart defaults while retaining native Streamlit controls and research limitations. Refer to `PHASE3_DELIVERY.md` for applied page-level changes, offline preflight and local browser QA still required. No deployment or new forecasting work was performed.
