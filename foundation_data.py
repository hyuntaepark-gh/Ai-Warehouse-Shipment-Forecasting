"""Read only lightweight verified summaries; no dependency on private raw files."""
from pathlib import Path
import hashlib
import json
import pandas as pd
import streamlit as st

SUMMARY_DIR=Path(__file__).resolve().parent/'foundation_summaries'
CLARIFICATION='Raw source audit found 53 records on six dates in January 2017 across three warehouses. These sparse records do not supply complete warehouse-week outcomes for the archived 12-week forecasts; projected-period accuracy remains unevaluated.'


def clarify_2017(text):
    """Correct an inherited narrative without changing frozen numerical contracts."""
    return text.replace('Observed 2017 outcomes are unavailable, so this does not directly validate future forecasts.',CLARIFICATION)


@st.cache_data(show_spinner=False)
def load_foundation(directory=None):
    root=Path(directory) if directory else SUMMARY_DIR
    info=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    if info.get('schema_version')!=1:raise ValueError('Unsupported data summary version')
    tables={}
    for name,meta in info['summary_files'].items():
        path=(root/name).resolve()
        if not path.is_relative_to(root.resolve()) or path.suffix!='.csv':raise ValueError('Invalid summary path')
        content=path.read_bytes()
        if hashlib.sha256(content).hexdigest()!=meta['sha256']:raise ValueError('Summary integrity mismatch: '+name)
        tables[path.stem]=pd.read_csv(path)
    return info,tables
