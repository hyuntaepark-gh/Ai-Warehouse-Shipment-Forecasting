"""Validate the exact reviewed Forecast Horizons payload before it can be displayed."""

from base64 import b64decode, b64encode
from pathlib import Path
import json

from deployment.validate_public_data_package import (
    SPEC, digest, inventory, json_bytes, require_authorization, review_payload,
)

PROFILE = "horizons"
SECRET_FILE = Path("/etc/secrets/warehouse-iq-horizons.json")
ATTRIBUTION_REVISION = "warehouse-iq-horizons-v1"
MAX_ENVELOPE_BYTES = 65_536


def check_host_authorization(record, service_id, spec_path=SPEC):
    spec = spec_path.read_bytes()
    plan = json.loads(spec)["profiles"][PROFILE]
    require_authorization(record, PROFILE, "host_storage", plan, digest(spec))
    if (not service_id or record.get("render_service_id") != service_id
            or record.get("attribution_revision") != ATTRIBUTION_REVISION):
        raise ValueError("The decision must cover this Render service and the displayed attribution.")
    return plan


def load_approved_pilot(env, secret_file=SECRET_FILE, spec_path=SPEC):
    # There is deliberately no fallback to the project, local data, or a preview service.
    service_id = env.get("RENDER_SERVICE_ID")
    if (env.get("WIQ_RELEASE_MODE") != "horizons_display" or env.get("RENDER") != "true"
            or env.get("IS_PULL_REQUEST") != "false" or not service_id):
        return None
    try:
        with secret_file.open("rb") as stream:
            raw = stream.read(MAX_ENVELOPE_BYTES + 1)
        if len(raw) > MAX_ENVELOPE_BYTES:
            return None
        envelope = json.loads(raw)
        if not isinstance(envelope, dict) or set(envelope) != {"authorization", "files"}:
            return None
        plan = check_host_authorization(envelope["authorization"], service_id, spec_path)
        objects = envelope["files"]
        if not isinstance(objects, dict) or objects.keys() != plan["files"].keys():
            return None
        payload = {name: b64decode(content, validate=True) for name, content in objects.items()}
        return payload if inventory(payload) == plan["files"] else None
    except (OSError, ValueError, TypeError, KeyError):
        return None


def prepare_host_envelope(authorization, destination):
    record = json.loads(authorization.read_bytes())
    service_id = record.get("render_service_id") if isinstance(record, dict) else None
    plan = check_host_authorization(record, service_id)
    payload = review_payload(PROFILE)
    if inventory(payload) != plan["files"]:
        raise ValueError("The prepared files differ from the reviewed pilot profile.")
    envelope = json_bytes({
        "authorization": record,
        "files": {name: b64encode(data).decode("ascii") for name, data in payload.items()},
    })
    if len(envelope) > MAX_ENVELOPE_BYTES:
        raise ValueError("The Render secret file exceeds the pilot envelope limit.")
    with destination.open("xb") as stream:
        stream.write(envelope)
