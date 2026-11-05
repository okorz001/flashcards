#!/usr/bin/env python3
"""Decide whether a GitHub event may start an agent run, per docs/agent-workflow.md."""
import json
import os
import re
import subprocess
import sys
from typing import NamedTuple

TRIGGER_LABEL = "ready-for-agent"
COLLABORATOR_ASSOCIATIONS = ("OWNER", "COLLABORATOR")
COLLABORATOR_ROLES = ("admin", "maintain", "write")
AGENT_STATUS_LABELS = ("with-agent", "agent-failed")
ISSUE_BRANCH = re.compile(r"^issue-(\d+)/")

NOT_COLLABORATOR_COMMENT = (
    f"Removed `{TRIGGER_LABEL}`: agents only work on issues opened by a collaborator."
)
OPEN_PR_COMMENT = (
    "This issue already has an open PR, so no run was started. "
    "A review on the PR starts the next run."
)


class Decision(NamedTuple):
    action: str  # skip | run | remove_label | move_to_with_agent
    task: str | None = None
    issue: int | None = None


def issue_for_branch(head_ref: str, head_repo: str | None, repo: str) -> int | None:
    match = ISSUE_BRANCH.match(head_ref)
    if match is None or head_repo != repo:
        return None
    return int(match.group(1))


def has_open_issue_pr(prs: list[dict], issue: int) -> bool:
    return any(
        not pr["isCrossRepository"] and pr["headRefName"].startswith(f"issue-{issue}/")
        for pr in prs
    )


def decide_label(
    sender_role: str, issue_association: str, issue: int, has_open_pr: bool
) -> Decision:
    if sender_role not in COLLABORATOR_ROLES:
        return Decision("skip")
    if issue_association not in COLLABORATOR_ASSOCIATIONS:
        return Decision("remove_label", issue=issue)
    if has_open_pr:
        return Decision("move_to_with_agent", issue=issue)
    return Decision("run", "implement", issue)


def decide_review(
    state: str, reviewer_association: str, issue: int | None, issue_labels: list[str]
) -> Decision:
    if state.lower() == "approved":
        return Decision("skip")
    if reviewer_association not in COLLABORATOR_ASSOCIATIONS:
        return Decision("skip")
    if issue is None:
        return Decision("skip")
    if not any(label in AGENT_STATUS_LABELS for label in issue_labels):
        return Decision("skip")
    return Decision("run", "review", issue)


class GhError(Exception):
    pass


def gh(*args: str) -> str:
    result = subprocess.run(["gh", *args], capture_output=True, text=True)
    if result.returncode != 0:
        raise GhError(f"gh {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout


def sender_role(repo: str, login: str) -> str:
    try:
        return gh("api", f"repos/{repo}/collaborators/{login}/permission", "--jq", ".role_name").strip()
    except GhError as error:
        if "HTTP 404" in str(error):
            return "none"
        raise


def open_prs(repo: str) -> list[dict]:
    out = gh(
        "pr", "list", "--repo", repo, "--state", "open", "--limit", "100",
        "--json", "headRefName,isCrossRepository",
    )
    return json.loads(out)


def issue_labels(repo: str, issue: int) -> list[str]:
    return json.loads(gh("api", f"repos/{repo}/issues/{issue}", "--jq", "[.labels[].name]"))


def decide_label_event(event: dict, repo: str) -> Decision:
    if event["label"]["name"] != TRIGGER_LABEL:
        return Decision("skip")
    issue = event["issue"]
    role = sender_role(repo, event["sender"]["login"])
    has_open_pr = has_open_issue_pr(open_prs(repo), issue["number"])
    return decide_label(role, issue["author_association"], issue["number"], has_open_pr)


def decide_review_event(event: dict, repo: str) -> Decision:
    head = event["pull_request"]["head"]
    head_repo = (head.get("repo") or {}).get("full_name")
    issue = issue_for_branch(head["ref"], head_repo, repo)
    labels = issue_labels(repo, issue) if issue is not None else []
    review = event["review"]
    return decide_review(review["state"], review["author_association"], issue, labels)


def apply(decision: Decision, repo: str) -> None:
    issue = str(decision.issue)
    if decision.action == "remove_label":
        gh("issue", "edit", issue, "--repo", repo, "--remove-label", TRIGGER_LABEL)
        gh("issue", "comment", issue, "--repo", repo, "--body", NOT_COLLABORATOR_COMMENT)
    elif decision.action == "move_to_with_agent":
        gh("issue", "edit", issue, "--repo", repo, "--remove-label", TRIGGER_LABEL)
        gh("issue", "edit", issue, "--repo", repo, "--add-label", "with-agent")
        gh("issue", "comment", issue, "--repo", repo, "--body", OPEN_PR_COMMENT)


def write_outputs(decision: Decision) -> None:
    run = decision.action == "run"
    lines = [f"task={decision.task if run else ''}", f"issue={decision.issue if run else ''}"]
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a") as f:
            f.write("\n".join(lines) + "\n")
    print(decision)


def main() -> None:
    repo = os.environ["REPO"]
    with open(os.environ["GITHUB_EVENT_PATH"]) as f:
        event = json.load(f)

    event_name = os.environ["GITHUB_EVENT_NAME"]
    if event_name == "issues":
        decision = decide_label_event(event, repo)
    elif event_name == "pull_request_review":
        decision = decide_review_event(event, repo)
    else:
        sys.exit(f"Unexpected event: {event_name}")

    apply(decision, repo)
    write_outputs(decision)


if __name__ == "__main__":
    try:
        main()
    except GhError as error:
        sys.exit(str(error))
