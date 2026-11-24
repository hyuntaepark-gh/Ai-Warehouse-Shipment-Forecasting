"""Prepare and load the independently reviewed CFS Area display-only section."""

import argparse
import json
import re
from pathlib import Path

from deployment.page_publication import cfs_area_plan
from deployment.render_payload import load_render_payload, write_render_payload
from deployment.validate_public_data_package import ROOT, validate_package

LOCAL_PACKAGE = ROOT / "runtime" / "cfs-area-coverage"
SECRET_FILE = Path("/etc/secrets/warehouse-iq-cfs-area.json")


def check_host_authorization(record, service_id):
    plan = cfs_area_plan()
    plan.validate(record, service_id=service_id)
    return plan


def load_approved_cfs(env, secret_file=None):
    commit = env.get("RENDER_GIT_COMMIT", "")
    if not re.fullmatch("[a-f0-9]{40}", commit):
        return None

    def authorize(record, service_id):
        plan = check_host_authorization(record, service_id)
        if record.get("deployed_commit") != commit:
            raise ValueError("CFS approval does not cover this deployed commit.")
        return plan

    return load_render_payload(env, SECRET_FILE if secret_file is None else secret_file,
                               authorize, modes={"public"})


def prepare_cfs_envelope(authorization, destination, *, package=LOCAL_PACKAGE):
    record = json.loads(authorization.read_bytes())
    service_id = record.get("render_service_id") if isinstance(record, dict) else None
    plan = check_host_authorization(record, service_id)
    if not re.fullmatch("[a-f0-9]{40}", record.get("deployed_commit", "")):
        raise ValueError("The CFS decision must identify the verified deployment SHA.")
    write_render_payload(destination, record, validate_package(package, {"files": plan.files}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("authorization", type=Path, help="Existing human hosting and display decision")
    parser.add_argument("destination", type=Path, help="New private Render secret file")
    parser.add_argument("--package", type=Path, default=LOCAL_PACKAGE)
    args = parser.parse_args()
    try:
        prepare_cfs_envelope(args.authorization, args.destination, package=args.package)
    except (OSError, TypeError, ValueError, KeyError) as error:
        parser.exit(1, f"CFS Area release preparation failed: {error}\n")
    print("Prepared the private Render secret for the recorded CFS Area decision.")


if __name__ == "__main__":
    main()
