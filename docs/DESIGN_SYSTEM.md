# Public dashboard design

Warehouse IQ uses a wide layout, native Streamlit sidebar navigation, and readable chart controls. Shared typography and color live in `design_system.py` and `product_layout.py`. Route labels and sidebar behavior live in `navigation.py`.

Data Foundation renders the published CFS record coverage as a heatmap, with survey-year and transportation-mode filters. Hover shows the exact record counts. Blank cells represent combinations that are absent from the extract. The chart displays estimate-table coverage. Shipment totals, freight tonnage, transportation value and warehouse demand are outside its scope.

Held routes use a consistent status message. The chart renderer provides source attribution and no CSV output.
