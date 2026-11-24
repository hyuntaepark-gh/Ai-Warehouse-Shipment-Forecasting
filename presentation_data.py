"""Read-side cache for the archive inventory used by the portfolio interface."""

from pathlib import Path

import streamlit as st

from data_loading import inventory


@st.cache_data(show_spinner=False, max_entries=4)
def _inventory(directory, signature):
    # The signature is part of the cache key even though the reader takes a directory.
    return inventory(directory)


def cached_inventory(directory):
    root = Path(directory).resolve()
    files = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            stat = path.stat()
            files.append((path.relative_to(root).as_posix(), stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns))
    return _inventory(root, tuple(files))
