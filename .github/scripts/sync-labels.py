#!/usr/bin/env python3
"""Create or update the repo's status labels from .github/labels.json."""
import json
import os
import subprocess
import sys


def gh(*args: str) -> int:
    return subprocess.run(["gh", *args]).returncode


def main() -> None:
    repo = os.environ["REPO"]
    data_file = sys.argv[1] if len(sys.argv) > 1 else ".github/labels.json"
    with open(data_file) as f:
        data = json.load(f)

    for rename in data.get("renames", []):
        if gh("label", "edit", rename["from"], "--repo", repo, "--name", rename["to"]) == 0:
            print(f"Renamed {rename['from']} -> {rename['to']}")

    for label in data["labels"]:
        name, color, description = label["name"], label["color"], label["description"]
        if gh("label", "edit", name, "--repo", repo, "--color", color, "--description", description) == 0:
            print(f"Updated {name}")
        else:
            subprocess.run(
                ["gh", "label", "create", name, "--repo", repo, "--color", color, "--description", description],
                check=True,
            )
            print(f"Created {name}")


if __name__ == "__main__":
    main()
