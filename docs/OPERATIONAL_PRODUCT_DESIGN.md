# Operational Insights — product design reference

This redesign replaces the page's information architecture and visualization approach,
not just its theme. Only Operational Insights adopts the new components. The other six
page renderers and the existing shared theme are checked against a pre-edit code-hash
snapshot in `operational_redesign_code_baseline.json`.

## Ten-second reading path

1. Compact product navigation, page title and archived-origin badge.
2. Three evidence views: Planning outlook, Historical, Scenarios. These experiments are
   not merged. Warehouse pills and a 4/8/12-week segmented filter replace long selectors.
3. A one-sentence, source-derived finding and four KPIs: forecast quantity, projected
   warehouse-weeks above historical P90, selected warehouse coverage and horizon dates.
4. A warehouse threshold comparison beside a warehouse-by-week heatmap.
5. An interactive single-warehouse projection/reference detail panel.
6. Three distinct insight types: observed fact, archived projection, illustrative implication.
7. Full data, downloads, methods and research documentation on demand.

## Visual system and reusable components

`bi_components.py` supplies navigation, workspace header, KPI row, panel wrapper, chart
wrapper and insight-card grid. `operational_charts.py` supplies the source-based threshold
comparison, heatmap and warehouse detail figure. These components are reusable, but no
other page is migrated in this iteration. CSS is activated by `.st-key-ops_product` and
removed from the effective layout when another page renders.

| Element | Convention |
|---|---|
| Canvas / surface | Existing #f5f7fb canvas, white panels, subtle #e3e9f2 rules |
| Ink / primary accent | #192b44 navy / #2866c9 blue; no severity meaning |
| Primary KPI | Navy card with white value; context in #d2deed |
| Typography | System sans-serif; 30px page title, 32px KPI values, 17px panel headings, 14px charts, 12–13px supporting text |
| Spacing | 14–16px rhythm, 20–22px panel padding, 12px corners |
| Desktop | Max outer width 1440px, 32px horizontal padding; measured usable width 1376px at a 1440px viewport |
| Navigation | Compact product bar with a Navigate popover containing all seven destinations; legacy sidebar hidden only on this page |
| Filters | Accessible native pills/segmented controls, visible labels, explicit empty states |
| Mobile | Two KPI columns; filters and analytical panels stack; all four warehouse controls visible; chart annotations omitted to preserve readable tap/hover cells |

Charts use larger labels, concise titles, source-aware hover, responsive sizing, no
range sliders and no extra visible data-table toolbar in the primary analysis flow.
Full-precision tables and CSV downloads remain accessible in disclosures. Historical
and scenario selectors, monitoring flags, planning-loss/FVA views and original research
limitations remain available.

## Visualizations and integrity

**Warehouse comparison:** each bar is maximum exported Demand_to_P90_Ratio × 100 in the
selected horizon. A full track means equality with that warehouse's historical P90.
Rows are sorted by that descriptive ratio, not by invented risk or forecast accuracy.
Normal/Watch badges copy source labels and use identical neutral styling. Classification
rules are undocumented; no bar threshold is used to classify a warehouse.

**Weekly heatmap:** one cell per exported warehouse/week, using the original ratio × 100.
Blue is a continuous quantitative scale from 0 to 100% of P90, not severity categories.
Tooltips retain projected quantity, historical reference, weekly date and original
weekly category. No missing cells are filled. Black/white annotation text is chosen
from interpolated color luminance to meet 4.5:1 contrast; this is a display rule only.

**Warehouse detail:** two labeled series only — archived projected demand and the saved
historical P90 reference. P90 is not a prediction interval, observed 2017 outcome or
physical capacity. Its history/quantile methodology is not exported.

Visible material qualifications identify the Dec 25, 2016 origin, missing 2017 actuals,
illustrative label rules and the difference between P90 and measured capacity. The
full notebooks and operational constraints are unavailable. No new risk scores,
observations, capacity, staffing, uncertainty, financial savings or model performance
are generated. CSV download precision and all 87 source files are preserved.

## Before / after

Before: stacked explanatory cards and banners; radio controls; three metrics far below
the title; four-line technical plot; repeated table/source blocks.

After: compact workspace; four immediate KPIs; normalized warehouse comparison and
weekly mosaic; selected-warehouse investigation; concise evidence-type insight cards;
consolidated disclosures and retained downloads.

See `OPERATIONAL_PRODUCT_QA.md` for exact screenshot dimensions, interaction checks,
numerical validation, source hashes and automated test results.
