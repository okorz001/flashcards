# Scratch: Middle Ground

Temporary comparison file. Option 2: one issue state machine, plus a table of
the PR events the workflow reacts to.

## Issue State Machine

Each state is one status label on the issue. Transitions marked "PR merged" and
"PR closed without merging" are caused by [PR events](#pr-events).

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

## PR Events

A PR's own state is GitHub's (open, CI status, reviews, merged, closed), with no
labels. The workflow reacts to these events on a PR from an issue branch:

| PR Event                                           | Reaction                                                   |
| -------------------------------------------------- | ---------------------------------------------------------- |
| Agent opens the PR                                 | Agent waits for CI and fixes failures                      |
| Collaborator submits a review that is not approval | Review run, if the issue is `with-agent` or `agent-failed` |
| Collaborator approves                              | Nothing                                                    |
| Collaborator merges                                | Issue closes, branch deleted                               |
| Collaborator closes without merging                | Issue moves to `needs-triage`, branch deleted              |

Rules linking the two:

- An issue has at most one open PR.
- Only an issue that is `with-agent`, `agent-failed`, or `with-collaborator` can
  have an open PR.
- A closed issue has no open PR.
