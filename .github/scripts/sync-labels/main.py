#!/usr/bin/env python3
"""Create or update the repo's status labels from labels.json."""
import json
import os
import subprocess
import sys
from pathlib import Path


def gh(*args: str) -> bool:
    return subprocess.run(["gh", *args]).returncode == 0


def main() -> None:
    repo = os.environ["REPO"]
    default_data_file = Path(__file__).resolve().parents[2] / "labels.json"
    data_file = sys.argv[1] if len(sys.argv) > 1 else default_data_file
    with open(data_file) as f:
        data = json.load(f)

    for rename in data.get("renames", []):
        if gh("label", "edit", rename["from"], "--repo", repo, "--name", rename["to"]):
            print(f"Renamed {rename['from']} -> {rename['to']}")

    for label in data["labels"]:
        name, color, description = label["name"], label["color"], label["description"]
        if gh("label", "edit", name, "--repo", repo, "--color", color, "--description", description):
            print(f"Updated {name}")
        elif gh("label", "create", name, "--repo", repo, "--color", color, "--description", description):
            print(f"Created {name}")
        else:
            sys.exit(f"Failed to create label {name}")


if __name__ == "__main__":
    main()
