# Historical Demand Analysis — Phase 2, first page

Only the Historical Demand destination was implemented in this iteration. Executive
Overview and the seven-page sidebar retain their existing behavior and styling. The
remaining five analysis pages are placeholders.

## Sources and actual observation coverage

| CSV export | Columns used | Coverage | Treatment |
|---|---|---|---|
| timesfm_historical_weekly_predictions.csv | Date, Actual, Year, Evaluation, Model | 2014: Jan 5–Dec 28; 2015: Jan 4–Dec 27; 2016: Jan 3–Dec 25 | 468 model rows become 156 distinct actual-demand observations, 52 per year. Model is used only to understand repetition; predictions and errors are excluded. Conflicting repeated actuals are rejected. |
| hierarchical_warehouse_forecasts.csv | Week, Warehouse, Demand | Jan 10–Dec 25, 2016; four warehouses, 51 weeks each | 204 observed warehouse-weeks. XGBoost, Original_Nonnegative and Reconciled_Forecast values are excluded. Duplicate warehouse-weeks are rejected. |

The scope selector separates the aggregate export from the warehouse sample. No
warehouse filter appears for aggregate demand. Warehouse mode exposes only 2016 and
the four exported warehouses. Aggregate and warehouse totals are not combined or
compared as if their coverage were identical. The shorter multi-horizon and recursive
warehouse samples are not stitched into the 51-week common-period history.

## Features and interpretation

- Actual-demand trend with weekly, monthly, quarterly and annual aggregation choices.
- Year selection, warehouse selection where supported, and empty-selection guidance.
- Annual/quarterly/monthly comparisons with observed-week counts in hover and downloads.
- Seasonality heatmap: mean weekly actual demand by recorded month, year and series.
  Means reduce the effect of different counts of recorded weeks per month. Missing
  cells remain blank. Hover reports the number of supporting observations.
- Box plots with each weekly observation, plus sample standard deviation, minimum,
  maximum, mean and coefficient of variation (CV) for each series/year.
- Coverage tables, CSV downloads, source references and explanation beside each chart.

All values are actual demand or descriptive aggregations of actual demand. No forecast
values, error metrics, training or seasonal-model fitting are used. CV uses sample
standard deviation (n−1) divided by mean weekly demand; it is undefined for fewer than
two observations or a nonpositive mean. The highest-CV sentence compares selected
series/year samples only and does not make a forecast-quality claim.

## Aggregation and missing information

Month and quarter buckets assign the entire weekly value to the period containing its
recorded timestamp. These are not exact daily calendar-month/quarter transaction
totals. Annual sums likewise summarize exported weekly samples. The warehouse sample
is explicitly partial: January is shorter and Q1 contains 12 observations per warehouse.

No missing demand is zero-filled or interpolated. Downloaded tables contain only
observed buckets. Trend rendering adds null separators at gaps so the line does not
connect unselected years or missing periods; separators are not observations and do
not enter statistics or downloads. Coverage gap counts describe intervals inside the
exported span, not completeness outside it.

The exports do not provide full 2012–2013 actual history, raw daily transactions,
product/category-level demand series or a complete multi-year warehouse history.
Those analyses require the original raw dataset. Demand is order demand, not verified
shipments, inventory, staffing or physical capacity. Descriptive patterns over three
aggregate years or one partial warehouse year do not establish stable recurring
seasonality. Evaluation-year labels remain visible in coverage and hover; no forecasting
results are pooled across retrospective and holdout periods on this page.

## Verification

`python -m unittest discover -s tests -v`: **27 tests passed** (18 existing checks and
9 new historical-page/data checks). Existing navigation tests were updated to expect
the implemented page and its missing-source state rather than a placeholder.

New checks cover actual-only deduplication, every aggregation level, agreement with
the existing monthly actual-total export, partial warehouse coverage, seasonal weekly
means, sample CV, gap behavior, conflicting/invalid inputs, year/scope/warehouse filters,
empty selections and rendering all four charts. The existing SHA-256 check confirms all
87 original capstone files still match the preimplementation baseline.

Restarted the Streamlit server at http://127.0.0.1:8501 and confirmed HTTP 200 / `ok`
from its health endpoint. Browser inspection confirmed Historical Demand navigation,
actual-only scope, source references and filters render correctly in the available
narrow preview. Desktop visual review across additional viewport sizes remains useful
before public deployment.
