"""Exact Data Foundation publication scope and its owner authorization checks."""
from dataclasses import dataclass
import json
from pathlib import Path

from deployment.validate_public_data_package import ROOT, digest, require_authorization

DISPLAY_REVISION = "v1"

CFS_PROFILE = "cfs_area_coverage"

CFS_RELEASE_CHECKS = {
    "owner_decision": "documented",
    "artifacts": "verified",
    "production_service": "verified",
    "repository_remediation": "resolved",
    "deployment_authorization": "activated",
}

@dataclass(frozen=True)
class PagePublication:
    page: str
    profile: str
    spec_sha256: str
    files: dict
    download_scopes: dict
    attribution_revision: str | None = None
    section_display_scope: str | None = None

    @property
    def display_scope(self):
        return self.section_display_scope or f"{self.page}/{DISPLAY_REVISION}/source-precision-charts-and-tables"

    def validate(self, record, *, service_id):
        """Require explicit hosting and browser display for this page and service."""
        plan = {"files": self.files, "download_scopes": self.download_scopes}
        require_authorization(record, self.profile, "host_storage", plan, self.spec_sha256)
        display = record.get("display")
        if (not service_id or record.get("render_service_id") != service_id
                or record.get("page") != self.page
                or not isinstance(display, dict) or display.get("scope") != self.display_scope
                or not isinstance(display.get("evidence_reference"), str)
                or not display["evidence_reference"].strip()):
            raise ValueError("The decision must cover this page, its source-precision display and this service.")
        if self.attribution_revision and record.get("attribution_revision") != self.attribution_revision:
            raise ValueError("The decision must cover the reviewed source attribution.")
        if self.profile == CFS_PROFILE:
            references = ("final_release_reference", "repository_remediation_reference")
            if (record.get("release_checks") != CFS_RELEASE_CHECKS
                    or any(not isinstance(record.get(key), str) or not record[key].strip() for key in references)):
                raise ValueError("CFS requires resolved prerequisites and recorded final owner release authorization.")
            if any(set(grant["channels"]) != {"host_storage", "public_display"}
                   for grant in record["files"].values()):
                raise ValueError("The CFS pilot authorizes only hosting and browser display.")

    def validate_git(self, record, *, repository):
        """Check GitHub distribution separately from hosting and display."""
        if self.profile == CFS_PROFILE:
            raise ValueError("Public Git distribution of the CFS pilot files is denied.")
        plan = {"files": self.files, "download_scopes": self.download_scopes}
        require_authorization(record, self.profile, "public_git", plan, self.spec_sha256)
        if not repository or record.get("page") != self.page or record.get("github_repository") != repository:
            raise ValueError("The Git decision must name the page and exact repository.")

def cfs_area_plan():
    """Read the section plan without changing the other Data Foundation dependencies."""
    source = (ROOT / "docs" / "cfs_area_coverage_package.json").read_bytes()
    scope = json.loads(source)
    return PagePublication(scope["page"], scope["profile"], digest(source), scope["files"], scope["download_scopes"],
                           attribution_revision=scope["attribution_revision"],
                           section_display_scope=scope["display_scope"])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("page", help="Exact dashboard page title")
    parser.add_argument("--section", choices=("cfs-area-coverage",), help="Check a section independently of its page")
    parser.add_argument("--authorization", type=Path, help="Read an existing human decision")
    destination = parser.add_mutually_exclusive_group()
    destination.add_argument("--service-id", help="Render service for hosting and browser display")
    destination.add_argument("--github-repository", help="Exact GitHub owner/repository for distribution")
    args = parser.parse_args()
    if bool(args.authorization) != bool(args.service_id or args.github_repository):
        parser.error("Supply the existing decision and exactly one release destination.")
    try:
        plan = cfs_area_plan()
        if plan.page != args.page:
            raise ValueError("The section is outside the requested page.")
        if args.authorization:
            record = json.loads(args.authorization.read_bytes())
            if args.service_id:
                plan.validate(record, service_id=args.service_id)
            else:
                plan.validate_git(record, repository=args.github_repository)
            print("The recorded decision matches this page and destination. No files were released.")
            raise SystemExit(0)
    except (OSError, ValueError, TypeError, KeyError) as error:
        parser.exit(1, f"Page plan unavailable: {error}\n")
    print(json.dumps({"page": plan.page, "profile": plan.profile, "package_spec_sha256": plan.spec_sha256,
                      "display_scope": plan.display_scope, "attribution_revision": plan.attribution_revision,
                      "files": plan.files,
                      "download_scopes": plan.download_scopes}, indent=2))
