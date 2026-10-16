# Scratch: Separate State Machines

Temporary comparison file. Option 1: an issue state machine and a PR state
machine, each with its own diagram.

## Issue State Machine

Each state is one status label on the issue. Transitions marked "PR merged" and
"PR closed without merging" are caused by the
[PR state machine](#pr-state-machine).

```mermaid
stateDiagram-v2
    [*] --> NeedsTriage: Collaborator or agent opens issue
    [*] --> ReadyForAgent: Collaborator opens a fully planned issue
    [*] --> ExternalReport: Anyone else opens issue
    ExternalReport --> [*]: Fixed by a linked issue, or declined

    NeedsTriage --> ReadyForAgent: Collaborator writes plan
    NeedsTriage --> [*]: Collaborator closes as not planned
    ReadyForAgent --> WithAgent: Agent starts
    WithAgent --> Blocked: Agent has a question
    WithAgent --> Failed: Run fails
    WithAgent --> WithCollaborator: Agent stops early
    Blocked --> ReadyForAgent: Collaborator updates plan
    Blocked --> [*]: Collaborator closes as not planned
    Failed --> ReadyForAgent: Collaborator retries without a PR
    Failed --> WithAgent: Collaborator retries with a review

    NeedsTriage --> WithCollaborator: Collaborator takes over
    ReadyForAgent --> WithCollaborator: Collaborator takes over
    WithAgent --> WithCollaborator: Collaborator takes over
    Blocked --> WithCollaborator: Collaborator takes over
    Failed --> WithCollaborator: Collaborator takes over
    WithCollaborator --> ReadyForAgent: Collaborator hands back without a PR
    WithCollaborator --> WithAgent: Collaborator hands back with a PR
    WithCollaborator --> [*]: Collaborator closes issue

    WithAgent --> [*]: PR merged
    WithCollaborator --> [*]: PR merged
    WithAgent --> NeedsTriage: PR closed without merging
    WithCollaborator --> NeedsTriage: PR closed without merging
    Failed --> NeedsTriage: PR closed without merging

    NeedsTriage: needs-triage
    ReadyForAgent: ready-for-agent
    WithAgent: with-agent
    Blocked: agent-blocked
    Failed: agent-failed
    WithCollaborator: with-collaborator
    ExternalReport: external-report
```

## PR State Machine

PR states are GitHub's own, not labels. Each transition is an event that the
workflow reacts to.

```mermaid
stateDiagram-v2
    [*] --> CIRunning: Agent or collaborator opens PR from an issue branch
    CIRunning --> CIFailed: CI fails
    CIRunning --> AwaitingReview: CI passes
    CIFailed --> CIRunning: Agent or collaborator pushes a fix
    AwaitingReview --> AddressingReview: Collaborator submits a review that is not an approval
    AddressingReview --> CIRunning: Agent pushes fixes
    AddressingReview --> AwaitingReview: Agent replies without changes
    AwaitingReview --> Approved: Collaborator approves
    Approved --> CIRunning: Anyone pushes
    Approved --> Merged: Collaborator merges
    AwaitingReview --> Closed: Collaborator closes without merging
    CIFailed --> Closed: Collaborator closes without merging
    Merged --> [*]: Issue closes, branch deleted
    Closed --> [*]: Issue to needs-triage, branch deleted

    CIRunning: CI running
    CIFailed: CI failed
    AwaitingReview: Awaiting review
    AddressingReview: Review run in progress
```

Rules linking the two:

- An issue has at most one open PR.
- Only an issue that is `with-agent`, `agent-failed`, or `with-collaborator` can
  have an open PR.
- A closed issue has no open PR.
