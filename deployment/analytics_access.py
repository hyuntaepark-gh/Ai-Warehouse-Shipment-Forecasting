"""Bind approved bytes to one request and keep data off Git and static URLs."""
from contextlib import contextmanager
from contextvars import ContextVar
import json
from pathlib import Path
import re
import tempfile

import streamlit as st

from deployment.page_publication import PagePublication
from deployment.validate_public_data_package import ROOT, digest, validate_package

_MANIFEST = ROOT / "docs" / "analytical_runtime_pins.json"
_SCOPES = ROOT / "docs" / "evidence_scope_pins.json"
_APPROVALS = Path("/etc/secrets/warehouse-iq-analytical-approvals.json")
_PRIVATE_MOUNT = Path("/var/data/warehouse-iq")
_context = ContextVar("approved_analytics", default=None)
_scope = ContextVar("approved_evidence_scope", default=None)


def display_only():
    return _context.get() is not None


def selected(field):
    return (_scope.get() or {}).get(field)


def retail_datasets(default):
    fixed = selected("dataset")
    return (fixed,) if fixed else default


def evidence_scopes(page):
    records = json.loads(_SCOPES.read_bytes())
    return {key: record for key, record in records.items() if record["page"] == page}


def data_path(relative, local):
    active = _context.get()
    return active / relative if active is not None else local


def table_view(data=None, *args, **kwargs):
    if not display_only():
        return st.dataframe(data, *args, **kwargs)
    if isinstance(data, list) and data and isinstance(data[0], str):
        data = {"Result": data}
    options = {key: kwargs[key] for key in ("width", "hide_index", "alt") if key in kwargs}
    st.table(data, **options)


def download_view(*args, **kwargs):
    if not display_only():
        return st.download_button(*args, **kwargs)


def approved_payload(page, env, *, approvals=_APPROVALS, private_mount=_PRIVATE_MOUNT):
    service_id = env.get("RENDER_SERVICE_ID")
    commit = env.get("RENDER_GIT_COMMIT", "")
    if (env.get("WIQ_RELEASE_MODE") != "public" or env.get("RENDER") != "true"
            or env.get("IS_PULL_REQUEST") != "false" or not service_id
            or not re.fullmatch("[a-f0-9]{40}", commit)):
        return None
    try:
        raw = _MANIFEST.read_bytes()
        scope = json.loads(raw).get(page)
        if scope is None:
            raw = _SCOPES.read_bytes()
            scope = json.loads(raw)[page]
        plan = PagePublication(scope.get("page", page), scope["profile"], digest(raw), scope["files"], {},
                               attribution_revision=scope["attribution_revision"],
                               section_display_scope=scope["display_scope"])
        with approvals.open("rb") as stream:
            decision_bytes = stream.read(262_145)
        if len(decision_bytes) > 262_144:
            return None
        records = json.loads(decision_bytes)
        record = records[page]
        plan.validate(record, service_id=service_id)
        if (record.get("deployed_commit") != commit
                or not isinstance(record.get("final_release_reference"), str)
                or not record["final_release_reference"].strip()
                or any(set(grant["channels"]) != {"host_storage", "public_display"}
                       for grant in record["files"].values())):
            return None
        scope_root = private_mount / plan.profile
        if scope_root.resolve() != scope_root.absolute():
            return None
        return validate_package(scope_root, {"files": plan.files})
    except (OSError, ValueError, TypeError, KeyError, RecursionError):
        return None


@contextmanager
def render_inputs(payload, *, selection=None):
    """Use only the bytes returned by the gate, with no other route's files."""
    with tempfile.TemporaryDirectory(prefix="warehouse-iq-route-") as scratch:
        directory = Path(scratch)
        for name, contents in payload.items():
            path = directory / name  # Payload paths come from the validated package spec.
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(contents)
        token = _context.set(directory)
        scope_token = _scope.set(selection)
        try:
            yield
        finally:
            _scope.reset(scope_token)
            _context.reset(token)
