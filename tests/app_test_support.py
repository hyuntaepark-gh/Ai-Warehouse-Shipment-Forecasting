"""Start legacy page tests in the warehouse track explicitly."""

from hashlib import sha256
from html import unescape
import re

from streamlit.testing.v1 import AppTest

from data_loading import ROOT
from navigation import WAREHOUSE_HOME


def calculation_digest(path):
    """Hash a calculation module in the LF form stored in Git."""
    return sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def warehouse_app():
    app = AppTest.from_file(str(ROOT / "app.py"))
    app.session_state["navigation"] = WAREHOUSE_HOME
    return app.run(timeout=30)


def summary_cards(app):
    return {
        unescape(label): unescape(value)
        for entry in app.markdown if 'class="wiq-mini-grid"' in entry.value
        for label, value in re.findall(r"<small>(.*?)</small><b>(.*?)</b>", entry.value)
    }
