#!/usr/bin/env python3
"""Set an issue's status label on open or reopen, per docs/agent-workflow.md."""
import json
import os
import subprocess
import sys
from pathlib import Path

LABELS_FILE = Path(__file__).resolve().parents[2] / "labels.json"
COLLABORATOR_ASSOCIATIONS = ("OWNER", "COLLABORATOR")


def gh(*args: str) -> bool:
    return subprocess.run(["gh", *args]).returncode == 0


def status_labels() -> list[str]:
    with open(LABELS_FILE) as f:
        return [label["name"] for label in json.load(f)["labels"]]


def main() -> None:
    repo = os.environ["REPO"]
    issue = os.environ["ISSUE"]
    is_collaborator = os.environ["ASSOCIATION"] in COLLABORATOR_ASSOCIATIONS
    label = "needs-triage" if is_collaborator else "external-report"

    edit_args = []
    for name in status_labels():
        if name != label:
            edit_args += ["--remove-label", name]
    if not gh("issue", "edit", issue, "--repo", repo, *edit_args, "--add-label", label):
        sys.exit(f"Failed to set {label} on issue {issue}")

    if os.environ["ACTION"] == "reopened":
        if not gh("issue", "comment", issue, "--repo", repo, "--body", "This issue was reopened."):
            sys.exit(f"Failed to comment on issue {issue}")


if __name__ == "__main__":
    main()
