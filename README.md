# Warehouse IQ · Demand Intelligence

Warehouse IQ is a read-only Streamlit portfolio for two retrospective Capstone studies. It began as the Supply Chain Analytics Dashboard and now offers two separate research workspaces.

- **Final Research** explores forecasting horizons, model strategies, numerical stability and validation for recorded sales from M5 and Corporación Favorita.
- **Original Warehouse Operations** covers historical order demand, warehouse comparisons, model evaluations and archived planning projections. The projections originate in December 2016.

Research Overview is the home page. The sidebar lets you switch studies and keeps the last page for each study during the session. Retail sales and recorded orders are separate targets. Model scores belong to their own evaluation cohorts.

## Run locally

Use Python 3.12. Create and activate a virtual environment before installing dependencies.

~~~sh
python -m venv .venv
# Activate the virtual environment for your shell.
python -m pip install -r requirements.txt
python run_dashboard.py
python -m unittest discover -s tests -v
~~~

Visit [the local dashboard](http://127.0.0.1:8507/). The application reads authorized local inputs for its 13 pages and their local downloads. Missing data is shown as unavailable. It uses saved research results and does no model training or source downloads. [Runtime inputs by route](docs/public_release_manifest.json)

## Publication status

Research data publication remains pending. The root Render configuration starts a guarded preview showing page names and an availability notice. The separate Forecast Horizons configuration supports a display-only pilot after hosting and public display are approved for the exact payload. [Forecast Horizons release checklist](docs/FORECAST_HORIZONS_RELEASE_CHECKLIST.md)

The repository retains the legacy project history and inherited archive. Existing GitHub visibility does not establish permission for a new release. Build release artifacts from the allowlist and keep notebooks, raw data and approval evidence in private storage.

[M5 Forecasting – Accuracy](https://www.kaggle.com/competitions/m5-forecasting-accuracy) · [Corporación Favorita · Store Sales](https://www.kaggle.com/competitions/store-sales-time-series-forecasting) · [Historical Product Demand](https://www.kaggle.com/datasets/felixzhao/productdemandforecasting)
