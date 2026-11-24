"""Read a private Render secret with exact membership and byte pins."""

from base64 import b64decode, b64encode
import json

from deployment.validate_public_data_package import inventory, json_bytes

MAX_ENVELOPE_BYTES = 65_536


def load_render_payload(env, secret_file, authorize, *, modes):
    service_id = env.get("RENDER_SERVICE_ID")
    if (env.get("WIQ_RELEASE_MODE") not in modes or env.get("RENDER") != "true"
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
        plan = authorize(envelope["authorization"], service_id)
        files = envelope["files"]
        if not isinstance(files, dict) or files.keys() != plan.files.keys():
            return None
        payload = {name: b64decode(value, validate=True) for name, value in files.items()}
        return payload if inventory(payload) == plan.files else None
    except (OSError, ValueError, TypeError, KeyError, RecursionError):
        return None


def write_render_payload(destination, record, payload):
    envelope = json_bytes({
        "authorization": record,
        "files": {name: b64encode(data).decode("ascii") for name, data in payload.items()},
    })
    if len(envelope) > MAX_ENVELOPE_BYTES:
        raise ValueError("The Render secret file exceeds the envelope limit.")
    with destination.open("xb") as stream:
        stream.write(envelope)
