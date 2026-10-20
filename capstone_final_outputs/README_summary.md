# AI-Driven Demand Forecasting for Warehouse Operations Planning

## Project Overview

This project develops a multi-level demand forecasting
framework using historical product demand data.

The framework integrates statistical forecasting,
machine learning, deep learning benchmarks,
time-series foundation models, forecast uncertainty,
model interpretation, and warehouse operations planning.


## Forecasting Models and Analytical Methods

The analysis includes:

- ARIMA, SARIMA, SARIMAX, Prophet, and ETS
- TimesFM 3.0 zero-shot forecasting
- Random Forest, XGBoost, and LightGBM
- Weighted ensemble forecasting
- LSTM, GRU, N-BEATS, and N-HiTS exploratory benchmarks
- Warehouse-level demand forecasting
- Product category-level demand forecasting
- Forecast uncertainty and interval calibration
- High-demand risk analysis and forecast bias audits
- SHAP-based model explainability
- Multi-year time-series backtesting
- Feature ablation and multi-horizon evaluation
- Data-quality stress testing
- Hierarchical forecast reconciliation
- Forecast Value Added (FVA) analysis
- Statistical significance testing
- M5 external dataset validation
- Model monitoring and automated model selection
- Recursive multi-step forecasting validation


## Additional Full-Year Forecasting Results

As a follow-up to the statistical and deep learning
forecasting experiments, ETS and TimesFM 3.0 were
evaluated on the 2016 full-year holdout period.

The comparison uses the same 52-week forecasting
horizon and evaluates all models using:

- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)
- Weighted Absolute Percentage Error (WAPE)

### Full-Year Model Comparison

| Model | MAE | RMSE | WAPE (%) |
|---|---:|---:|---:|
| TimesFM 3.0 | 2,338,909.10 | 2,918,049.09 | 12.35% |
| ETS | 2,438,165.23 | 2,992,016.95 | 12.87% |
| SARIMAX | 2,665,392.55 | 3,283,772.14 | 14.07% |
| Refined SARIMA | 2,665,428.35 | 3,283,849.23 | 14.08% |
| Seasonal Naive | 3,550,721.48 | 4,353,584.14 | 18.75% |
| Prophet | 3,760,871.54 | 4,445,108.13 | 19.86% |
| N-BEATS | 4,019,328.04 | 4,670,975.39 | 21.22% |
| N-HiTS | 4,250,090.92 | 5,005,617.40 | 22.44% |

### Key Findings

TimesFM 3.0 achieved the lowest WAPE
in this experiment at 12.35%.

The selected ETS model achieved 12.87% WAPE.

The refined SARIMA model achieved
14.08% WAPE.

The results show that pretrained foundation models
and traditional exponential smoothing can provide
competitive forecasts for historical weekly demand.

However, the results are based on a single
2016 full-year holdout period.

Quarterly evaluation showed that forecasting
performance varied across different parts
of the year.

Retrospective 2014-2015 year-ahead results are
presented below to examine cross-year behavior.
Independent prospective validation would still be
needed to assess generalization more conclusively.

These full-year results should not be directly
compared with warehouse-level rolling forecasts,
because the forecasting horizons and evaluation
procedures differ.


## TimesFM Historical Year-Ahead Backtesting (2014-2015)

Two retrospective year-ahead forecast origins were added:
2014 uses the 2012-2013 history, and 2015 uses
2012-2014 history. The model is zero-shot on the
project's local data and is compared with the selected
ETS configuration and a seasonal naive benchmark.

### Results by Historical Validation Year

| Year | Model | MAE | RMSE | WAPE (%) |
|---|---|---:|---:|---:|
| 2014 | TimesFM 3.0 | 2,543,928.67 | 3,603,694.22 | 12.44% |
| 2014 | ETS | 2,686,561.42 | 3,360,438.17 | 13.14% |
| 2014 | Seasonal Naive | 2,839,482.63 | 3,576,906.52 | 13.88% |
| 2015 | ETS | 2,611,900.04 | 3,273,051.21 | 12.46% |
| 2015 | Seasonal Naive | 2,798,587.81 | 3,642,744.42 | 13.35% |
| 2015 | TimesFM 3.0 | 3,019,760.73 | 3,829,776.82 | 14.40% |

### Pooled Historical Validation Metrics

| Model | Weeks | MAE | RMSE | Pooled WAPE (%) |
|---|---:|---:|---:|---:|
| ETS | 104 | 2,649,230.73 | 3,317,032.48 | 12.79% |
| TimesFM 3.0 | 104 | 2,781,844.70 | 3,718,454.15 | 13.43% |
| Seasonal Naive | 104 | 2,819,035.22 | 3,609,975.57 | 13.61% |

The pooled WAPE calculation uses all 104 historical
validation weeks per model. These are retrospective
diagnostics, not a new untouched test set.

The ETS structure was selected using these same
2014 and 2015 folds, so the ETS backtest results
are post-selection and cannot be treated as independent
confirmation of superior generalization.

The 2016 forecasts remain a separate final holdout
reference. Performance comparisons across the
2014-2016 windows should be interpreted cautiously.


## Historical Quarterly Forecast Accuracy and Stability (2014-2016)

The quarterly analysis reuses the same weekly year-ahead
predictions, with no additional model training. The
2014-2015 quarters are retrospective diagnostic folds;
2016 is shown separately as a final holdout reference.

### Pooled 2014-2015 Quarterly WAPE

| Quarter | Model | Weeks | Pooled WAPE (%) |
|---|---|---:|---:|
| Q1 | Seasonal Naive | 26 | 15.11% |
| Q1 | ETS | 26 | 15.22% |
| Q1 | TimesFM 3.0 | 26 | 15.50% |
| Q2 | TimesFM 3.0 | 26 | 9.70% |
| Q2 | ETS | 26 | 10.83% |
| Q2 | Seasonal Naive | 26 | 11.22% |
| Q3 | ETS | 26 | 13.51% |
| Q3 | Seasonal Naive | 26 | 14.40% |
| Q3 | TimesFM 3.0 | 26 | 15.40% |
| Q4 | ETS | 26 | 11.58% |
| Q4 | TimesFM 3.0 | 26 | 13.13% |
| Q4 | Seasonal Naive | 26 | 13.70% |

### Quarterly Stability Diagnostics

| Model | Pooled quarterly WAPE range (pp) | Best year-quarter count (of 8) |
|---|---:|---:|
| Seasonal Naive | 3.89 | 0 |
| ETS | 4.39 | 4 |
| TimesFM 3.0 | 5.80 | 4 |

WAPE is recalculated from the actual weekly observations
in each quarterly subset rather than averaged across years.
Each historical year-quarter contains approximately 13 weeks;
pooled calendar quarters contain about 26 weeks.
The stability statistics are descriptive, not significance tests.
The ETS structure was selected using the same 2014-2015
folds and these results are not independent validation.


## Historical Monthly Forecast Performance (2014-2016)

The monthly analysis groups the existing 2014-2016
weekly year-ahead forecasts by the calendar month of
each recorded **weekly timestamp**. No monthly model
was separately trained or fitted.

### Pooled 2014-2015 Monthly Weekly WAPE

| Month | TimesFM 3.0 WAPE | ETS WAPE | Seasonal Naive WAPE |
|---|---:|---:|---:|
| Jan | 29.39% | 17.91% | 11.16% |
| Feb | 9.91% | 17.68% | 22.45% |
| Mar | 10.12% | 11.43% | 12.17% |
| Apr | 10.00% | 9.87% | 10.52% |
| May | 11.83% | 14.32% | 13.03% |
| Jun | 7.43% | 8.46% | 10.16% |
| Jul | 11.45% | 11.61% | 13.28% |
| Aug | 19.91% | 13.68% | 12.70% |
| Sep | 14.38% | 15.39% | 17.63% |
| Oct | 10.22% | 8.63% | 11.63% |
| Nov | 13.63% | 11.52% | 12.20% |
| Dec | 15.32% | 14.46% | 17.44% |

### Monthly Historical Stability Diagnostics

| Model | Pooled Monthly WAPE Range (pp) | Best Year-Month Count (of 24) |
|---|---:|---:|
| ETS | 9.44 | 8 |
| Seasonal Naive | 12.28 | 5 |
| TimesFM 3.0 | 21.96 | 11 |

These retrospective pooled WAPE values are recomputed
from weekly errors within each calendar month across
2014 and 2015, **not** from a simple average of monthly
percentage errors. The separately reported monthly-total
APE instead compares the sums of weekly predictions and
actual demand. Opposing weekly errors can cancel in
monthly totals, so the two measures have different meanings.

Only about 3-5 labeled weeks fall within an individual
calendar month. A weekly date is assigned wholly to its
recorded month even if the corresponding week crosses a
month boundary; these figures are **not exact calendar-month
daily transaction totals**. The 2016 month-level results
remain a separately labeled final holdout reference.
ETS configuration was chosen using the 2014-2015 folds,
and all month-level model comparisons are exploratory.


## Final Forecasting Framework

The final framework combines:

1. Overall demand monitoring
2. Warehouse-level demand forecasting
3. Product category-level forecasting
4. Forecast uncertainty estimation
5. Model explainability
6. Operational risk assessment
7. Illustrative capacity planning
8. Interactive forecasting dashboard


## Future Warehouse Demand Forecasting

The forecasting framework was extended to generate
recursive warehouse-level demand forecasts for
12 weeks beyond the final observed date.

The future forecasting process includes:

- Model refitting using available historical observations
- Recursive weekly demand forecasting
- Forecast generation without future observed demand
- Four-week demand planning summaries
- Eight-week demand planning summaries
- Twelve-week demand planning summaries
- Warehouse-level demand visualization

The forecasts begin after the final observed week
in December 2016 and represent a historical
forward-looking forecasting exercise.


## Historical Recursive Forecast Validation

A 12-week historical recursive backtest was conducted
using a forecast origin at the end of 2015.

The recursive XGBoost forecasting procedure was
evaluated against observed demand from early 2016.

A 52-week seasonal naive benchmark was included
to evaluate recursive forecasting performance.

Forecast accuracy was assessed using:

- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)
- Weighted Absolute Percentage Error (WAPE)
- Four-, eight-, and twelve-week cumulative evaluation windows

### Recursive Backtest Results

The historical recursive backtest included three
eligible warehouses and 36 warehouse-week observations.

At the 12-week evaluation horizon:

- Recursive XGBoost WAPE: 59.39%
- Seasonal Naive WAPE: 70.62%

At the individual warehouse level:

- Whse_A: XGBoost 103.20%, Seasonal Naive 32.11%
- Whse_C: XGBoost 42.64%, Seasonal Naive 49.04%
- Whse_S: XGBoost 66.72%, Seasonal Naive 95.05%

Whse_J was excluded from the historical recursive
backtest because the required 52 consecutive
weekly observations were not available before
the forecast origin.

Although recursive XGBoost achieved a lower
overall WAPE than the seasonal naive benchmark,
performance varied substantially across warehouses.

In particular, XGBoost performed considerably
worse than seasonal naive forecasting for Whse_A.

These findings demonstrate that recursive forecasting
does not consistently improve predictive accuracy
across individual warehouses.

Errors may accumulate or persist over longer
forecast horizons, limiting the reliability
of unvalidated future demand projections.

The historical recursive backtest provides a
retrospective diagnostic rather than independent
post-selection validation.

Its results should not be directly compared with
the original 2016 holdout results because the
forecasting procedures and evaluation samples differ.


## Operational Decision Support

Future warehouse demand forecasts were translated
into illustrative operational planning indicators.

The analysis includes:

- Historical high-demand threshold comparisons
- Warehouse-level demand risk classification
- Projected high-demand week identification
- Demand changes relative to recent historical levels
- Four-, eight-, and twelve-week planning summaries
- Illustrative warehouse operations recommendations

The operational decision framework connects
forecasting outputs with potential capacity
planning and demand monitoring decisions.

These recommendations are intended for
illustrative decision support rather than
validated operational deployment.


## Interactive Dashboard

An interactive warehouse forecasting dashboard
was developed to visualize historical test-period
demand, model predictions, high-demand thresholds,
and forecasting performance.

The dashboard is exported as a standalone HTML file.

Future demand forecasts and operational planning
summaries are provided as separate analysis outputs.


## External Validation

The forecasting methodology was also evaluated
using the independent M5 retail demand dataset.

This external validation examines the potential
generalizability of the forecasting approach
beyond the primary historical product demand dataset.


## Reproducibility

The analysis was developed using Python 3.12
and Jupyter Notebook within Visual Studio Code.

The project uses historical demand datasets
stored locally and generates forecasting tables,
visualizations, and dashboard outputs.

The primary source files include:

- Historical Product Demand.csv

The external validation uses:

- sales_train_evaluation.csv
- calendar.csv
- sell_prices.csv

Dataset paths and output directories may need
to be updated when reproducing the analysis
in a different computing environment.

All preprocessing, modeling, and evaluation steps
are documented in the project notebook.


## Key Research Limitations

The primary dataset contains recorded order demand
rather than confirmed outbound shipment volume.

The dataset does not contain actual warehouse
capacity, staffing requirements, inventory levels,
or verified operating costs.

Some forecasting benchmarks use different forecast
horizons or evaluation designs, so their performance
results are not directly interchangeable.

Repeated retrospective model comparisons using
the 2016 holdout are exploratory and do not
constitute independent post-selection validation.

The TimesFM full-year 2016 result uses one
historical holdout. Additional 2014-2015 retrospective
folds describe performance at earlier forecast origins,
but do not constitute independent post-selection
validation. The ETS model's configuration was selected
on the same historical folds used for this comparison.

Month-level evaluations contain only a few weekly
observations, depend on the recorded weekly timestamp
for calendar-month assignment, and do not represent
independent monthly model forecasts or exact monthly
transaction totals.

The historical recursive backtest included only
three eligible warehouses because one warehouse
had incomplete historical coverage.

Recursive forecast performance varied substantially
across warehouses, including poor performance
for Whse_A.

The recursive 12-week future forecasts originate
from December 2016 and do not represent current
real-time warehouse demand.

Observed 2017 demand is unavailable in the
source dataset, so the future forecasts cannot
be directly evaluated against actual outcomes.

Recursive forecasting may accumulate prediction
errors over longer forecast horizons.

Operational recommendations and capacity-planning
results are illustrative and should not be
interpreted as verified operational requirements
or measured financial savings.


## Conclusion

The project demonstrates how demand forecasting
methods can be integrated with uncertainty
assessment, model interpretation, and illustrative
warehouse operations planning.

The additional ETS and TimesFM experiments show
that multiple forecasting approaches can provide
competitive predictions for aggregate weekly demand.

However, forecasting performance varies by
model, prediction horizon, and evaluation design.

The historical recursive backtest highlights
the importance of warehouse-specific evaluation
before applying multi-step forecasts to
operational planning decisions.

The resulting framework provides a foundation
for future development of an automated forecasting
and operational decision-support platform.
