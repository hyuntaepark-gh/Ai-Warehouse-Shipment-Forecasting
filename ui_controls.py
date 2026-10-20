"""Compact, accessible dropdowns for the historical analytics dashboard.

Use a single stable selection instead of radio buttons. No calculations changed.
"""
import streamlit as st


def choice(label, options, *, index=0, horizontal=False, **kwargs):
    """Drop-in replacement for st.radio without radio-circle clutter.

    A named dropdown uses less space than a row of radio circles and cannot be
    cleared accidentally. Existing keys, labels, and default choices remain.
    """
    values = list(options)
    if not values:
        raise ValueError(f"{label}: no selection options")
    if not (0 <= index < len(values)):
        raise ValueError(f"{label}: index {index} outside available options")
    return st.selectbox(label, values, index=index, **kwargs)
