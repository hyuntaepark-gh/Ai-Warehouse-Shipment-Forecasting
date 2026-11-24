"""Explore counts of published CFS Area estimate records by survey year and mode."""

import csv
from dataclasses import dataclass
from io import StringIO
import json

import plotly.graph_objects as go
import streamlit as st

from deployment.validate_public_data_package import digest

CSV_FILE = "bts_cfs_area_record_coverage.csv"
REGISTRY_FILE = "candidate-cfs-area-coverage-registry.json"
HEADER = ("YEAR", "TMODE", "DMODE", "Population_Count")
COUNT_LABEL = "Published CFS estimate records"
SECTION_TITLE = "CFS Area Record Coverage"


@dataclass(frozen=True)
class CoverageRecord:
    year: int
    tmode: str
    dmode: str
    count: int


def parse_coverage(payload):
    source = json.loads(payload[REGISTRY_FILE])
    data = payload[CSV_FILE]
    if (source["dataset_id"] != "j246-y2rf" or source["csv"] != CSV_FILE
            or tuple(source["dimensions"]) != HEADER[:3] or source["units"] != "records"
            or source["csv_bytes"] != len(data) or source["csv_sha256"] != digest(data)):
        raise ValueError("The CFS Area registry does not match the coverage data.")
    reader = csv.reader(StringIO(data.decode("utf-8"), newline=""))
    if next(reader, None) != list(HEADER):
        raise ValueError("Unexpected CFS Area coverage columns.")
    rows = tuple(CoverageRecord(int(year), tmode, dmode, int(count))
                 for year, tmode, dmode, count in reader)
    keys = {(row.year, row.tmode, row.dmode) for row in rows}
    if (len(rows) != source["rows"] or len(keys) != len(rows)
            or sorted({row.year for row in rows}) != source["calendar_years"]
            or any(not row.tmode.isascii() or not row.tmode.isdecimal()
                   or not row.dmode.isascii() or not row.dmode.isdecimal()
                   or row.count <= 0 for row in rows)):
        raise ValueError("Unexpected CFS Area groups, survey years or record counts.")
    return source, rows


def coverage_chart(rows, years):
    """Place only source counts into cells. Missing year/mode pairs remain gaps."""
    modes = sorted({(row.tmode, row.dmode) for row in rows},
                   key=lambda pair: (int(pair[0]), int(pair[1])))
    counts = {(row.year, row.tmode, row.dmode): row.count for row in rows}
    cells = [[counts.get((year, tmode, dmode)) for year in years] for tmode, dmode in modes]
    labels = [f"{tmode} / {dmode}" for tmode, dmode in modes]
    fig = go.Figure(go.Heatmap(
        x=[str(year) for year in years], y=labels, z=cells,
        colorscale=[[0, "#e8f4f4"], [0.45, "#41999d"], [1, "#0a4f56"]],
        xgap=4, ygap=3, hoverongaps=False,
        hovertemplate=("Survey year %{x}<br>TMODE / DMODE %{y}<br>"
                       "%{z:,d} published CFS estimate records<extra></extra>"),
        colorbar={"title": {"text": "Records", "side": "top"}, "thickness": 12, "tickformat": "~s"},
    ))
    fig.update_layout(height=max(260, 125 + 24 * len(modes)), margin={"l": 8, "r": 8, "t": 8, "b": 42})
    fig.update_xaxes(title="Survey year", type="category", side="top", fixedrange=True)
    fig.update_yaxes(title="TMODE / DMODE", type="category", autorange="reversed", fixedrange=True)
    return fig


def render_coverage(source, rows):
    st.subheader(SECTION_TITLE)
    st.write("Explore how many published CFS estimate records appear in each survey year and transportation-mode grouping.")
    st.caption("Each cell counts rows in a federal estimate table. It does not measure shipments, freight tonnage, transportation value, warehouse demand, or shipment forecasts.")
    st.caption("Combined and detailed mode codes are shown as published. Record coverage may vary across years and mode pairs.")
    left, right = st.columns(2)
    with left:
        years = sorted(st.multiselect("Survey years", source["calendar_years"],
                                     default=source["calendar_years"], key="cfs_area_years"))
    with right:
        codes = sorted({row.tmode for row in rows}, key=int)
        code = st.selectbox("Transportation mode (TMODE)", [None, *codes], index=1,
                            format_func=lambda value: "All mode codes" if value is None else f"TMODE {value}",
                            key="cfs_area_tmode")
    selected = [row for row in rows if row.year in years and (code is None or row.tmode == code)]
    if selected:
        st.markdown("**Which survey years and mode categories have published records?**")
        st.plotly_chart(coverage_chart(selected, years), width="stretch", key="cfs_area_heatmap",
                        config={"displayModeBar": False, "scrollZoom": False})
        st.caption(f"{len(selected)} of {len(rows)} source groups shown. Hover for exact counts. "
                   "Blank cells indicate combinations absent from this extract.")
    else:
        st.info("Select one or more survey years with records for this transportation mode.")
    dataset_id = source["dataset_id"]
    title = source["title"].replace("2012-2022", "2012–2022")
    st.caption(f"[{title}](https://data.bts.gov/d/{dataset_id}) ({dataset_id}) · "
               "U.S. Census Bureau — Commodity Flow Survey · "
               "U.S. DOT Bureau of Transportation Statistics (BTS) · "
               f"Data snapshot {source['data_update_utc'][:10]}.")
