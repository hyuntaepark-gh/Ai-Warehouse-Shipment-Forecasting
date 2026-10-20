# Data Foundation: source audit and deployment

The eighth Warehouse IQ page explains raw source coverage separately from cleaned weekly samples and model evaluation. It preserves all seven analytical routes and the icon sidebar.

## Offline generation

Run locally with private inputs (never from Streamlit or Render startup):

```text
python build_foundation.py --raw-dir "./raw_data" --notebook "./private_data/MITA_Capstone_Week_15.ipynb" --capstone capstone_final_outputs
```

The four extracted CSV files are SHA-256 checked against their calendar.zip members and checked again after the build. The notebook hash and zero-based cell extracts document the actual preprocessing contract. The builder fails if inspected rules change. The runtime imports only foundation_data.py, never the builder; it validates and caches the approximately 229 KB of CSV/JSON summaries.

Missing dates are excluded; parentheses represent negative signed demand. Zeros, negatives, repeated rows and large demand values are retained. Date filters select 2012–2016, then 2 January 2012–25 December 2016 for Sunday-ending weekly sums. “Complete weeks” refers to calendar boundaries, not proven transaction completeness. Raw annual/monthly counts include all usable-date records and are never substituted with forecast-week sample counts.

## Research clarification

- Raw rows: 1,048,575; missing dates: 11,239; dated rows: 1,037,336.
- Date span: 8 January 2011–9 January 2017; 1,729 recorded dates across 2,194 calendar dates. No-record days are not necessarily lost data or zero demand.
- 122,423 extra exact repeated rows; no transaction ID establishes whether these are errors. 10,469 negative and 28,681 zero records are retained.
- Raw modeling years contain 1,036,643 rows; weekly source contains 1,034,979 rows, with 1,664 boundary rows excluded. The resulting 260 weeks exactly reproduce all 156 distinct 2014–2016 archived aggregate actuals, with maximum difference zero.
- 2017 contains 53 rows on six dates, 2–9 January, for 45 products and three warehouses (C/J/S), omitting A. The old blanket statement that no 2017 observations exist is incorrect. These records do not establish complete warehouse-week actuals for 1 January–19 March forecasts. No new accuracy score or changed model conclusion follows.
- 1,048,575 rows plus a header exactly equal Excel’s 1,048,576-row limit. The last CSV row is dated June 2016 and order is not chronological. Suspected export truncation is explicitly unconfirmed: no larger authoritative original or export log was supplied. Do not call 2012–2016 exhaustive or complete transactions. [Microsoft specification](https://support.microsoft.com/en-us/office/excel-specifications-and-limits-1672b34d-7043-467e-8e27-269d656771c3).

Original Capstone files and calculation modules remain unchanged. UI captions explicitly clarify 2017 coverage; the frozen comparison module’s inherited text is corrected at the display boundary. Original README wording remains archived rather than silently overwritten.

## M5 separation

30,490 item/store series, 3,049 items, 10 stores, 3 states, 3 categories and 7 departments. 1,941 observed sales days run from 29 January 2011 to 22 May 2016. Calendar has 1,969 days through 19 June 2016; later calendar dates are not observed sales. Prices contain 6,841,121 store/item/week rows.

The notebook aggregates sales to stores, maps d to date, retains 277 seven-day weeks, constructs past-only features with a 52-week warm-up, and uses the last 52 usable weeks for rolling one-week-ahead testing. Reconstructed test dates are 31 May 2015–22 May 2016. These source-rule dates do not retroactively assert that undated exported metrics encode those exact dates. Metrics stay on Forecast Reliability.

Although supplied and checked for existence, sell_prices is not read into the notebook’s M5 feature construction. Calendar events and SNAP columns are also not used in those features. No new pricing model or price-effect claim was added. A blank named-event field is not treated as a corrupted calendar date. Price key uniqueness is checked exactly with collision-free integer keys.

## Render implications

Ship foundation_summaries/ with app code and existing lightweight Capstone outputs. Keep the four large raw CSVs, ZIP and full notebook private; .gitignore now excludes their filenames and raw_data/private_data directories. No git commit or public upload is performed by this change. .gitignore does not remove previously tracked files: review tracked files before any future public push.

Build: `pip install -r requirements.txt`

Start (Render Linux shell): `python -m streamlit run app.py --server.address=0.0.0.0 --server.port=$PORT`

Health endpoint: `/_stcore/health`. Installed/required Streamlit 1.66 supports the existing native stateful popovers. No additional package is needed (NumPy is an existing pandas dependency used by offline generation only).

Do not put the offline summary builder in Render’s build/start command. Commit or otherwise bundle only the small verified summaries. Render expects a listener on 0.0.0.0 and PORT; its filesystem is ephemeral, so summaries must be part of each deployment artifact rather than generated only on a previous instance. No persistent disk is needed for these static summaries. Raw-data regeneration happens offline, followed by tests and replacement of the whole summary bundle.

[Render web services](https://render.com/docs/web-services) · [Render deployments and filesystem](https://render.com/docs/deploys)

A hosted Render deployment was not initiated; local application startup, tests and browser verification are separate from hosted deployment verification.