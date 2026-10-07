# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository.

## Project

A flashcards web app built with Next.js and TypeScript. It is fully statically
rendered (`output: "export"`), runs entirely in the browser with no backend, and
is deployed to GitHub Pages at https://flashcards.korz.org/.

## Working Agreement

This is a hobby project for experimenting with agentic development workflows.
Despite this, we aim for professional, production-quality standards. One
significant exception is to avoid unnecessary expense: prefer free tools and
services.

- **Follow the agreed plan.** Work is planned before it is marked
  `ready-for-work` (see GitHub below). Implement the plan in the issue. If the
  plan turns out to be wrong or incomplete, stop and raise it on the issue
  instead of improvising. For work requested outside an issue, propose a plan
  and get approval before implementing.
- **Treat the plan as literal.** When the plan says to copy, generate, or use
  something as-is, do exactly that. Do not remove, add, or modify parts of it.
  If something blocks or breaks the literal plan, stop and raise it on the issue
  with options and a recommendation. Do not work around it and report afterward.
- **Do not make arbitrary choices.** If a decision is not already settled by
  this file, the `docs/` directory, the issue, or existing code, ask. This
  includes adding or replacing a dependency, pinning or choosing a dependency
  version or config value the issue does not specify, choosing a library or
  tool, introducing a new convention or pattern, changing the data model or
  storage format, and UX or visual design decisions. Present the options with
  their tradeoffs and a recommendation, then wait for an answer.
- **Do not guess at requirements.** When a request is ambiguous, ask clarifying
  questions instead of filling gaps with assumptions.
- **Stay in scope.** Do not refactor, rename, or "improve" unrelated code as
  part of a change. File an issue instead (see GitHub below).
- **Ship code with tests.** Code changes include unit tests for the behavior
  they add or change, in the same change.
- **Do not open a PR for partial work.** If any part of the plan cannot be
  completed (blocked tool, denied permission, failing check), stop and report
  what is done and what is not. Partial work may be pushed to the branch, but a
  PR is opened only once the plan is fully implemented and all checks pass.
- **Report every deviation.** List any deviation from the plan, however small,
  in the PR description. If you would write "choices I made", you should have
  asked instead.

## Commands

| Script                 | Purpose                                         |
| ---------------------- | ----------------------------------------------- |
| `npm run dev`          | Start the development server                    |
| `npm run build`        | Build the static site into `out/`               |
| `npm run format`       | Format the repository with Prettier             |
| `npm run format:check` | Check formatting without changing files         |
| `npm run lint`         | Lint `src/` with ESLint, failing on any warning |
| `npm test`             | Run unit tests with Vitest                      |
| `npm run verify`       | Run format check, lint, test, and build         |

`npm run verify` must pass before proposing a code change.

## Commits

Commit titles are written in the imperative mood ("Add X", not "Added X") and
are 50 characters or fewer.

Omit the commit body unless it adds something the title cannot. Keep it brief
and hard wrapped at 72 characters. Information worth keeping belongs in the
repository (code comments or docs) or in the issue or PR discussion, not in
commit messages.

Do not add AI attribution to commits, such as `Co-Authored-By` or
`Claude-Session` trailers. Responsibility for a change belongs to whoever
approves and merges it.

## GitHub

### Issues

Work is tracked in GitHub issues. Each issue should be a single task that can be
completed in one PR. If an issue is too large for that, split it into
sub-issues, each completable in one PR.

Every issue is labeled as either `bug` or `enhancement`. Two more labels track
where an issue stands:

| Label            | Meaning                                                             |
| ---------------- | ------------------------------------------------------------------- |
| `needs-triage`   | Filed by an agent; not yet reviewed by a human                      |
| `ready-for-work` | Agreed to be legitimate, with a defined plan; agents may pick it up |

Label names use lowercase kebab-case (e.g. `needs-triage`).

Agents may only pick up issues labeled `ready-for-work`. Do not start work on an
issue without this label, even if it seems straightforward; ask instead.

Agents may file issues for work they discover but do not do as part of the
current change: bugs, refactors, or feature ideas. Every agent-filed issue must
have the `needs-triage` label, which is removed once a human has reviewed it.
Describe the problem or proposal and how it was found; for bugs, include how to
reproduce it if known. Do not act on it in the current change unless asked.

### Pull Requests

Every PR must reference the issue it completes using a closing keyword in the PR
description (e.g. `Closes #12`), so the issue closes automatically when the PR
merges.

Do not add AI attribution to PR descriptions or comments yourself. The GitHub
connector appends its own attribution footer, so adding another duplicates it.

When editing a PR description or comment that already has the GitHub
connector's attribution footer, never delete it. A full-body update (e.g.
replacing the whole description) must carry the existing footer forward.

Never rebase or force push a branch that has an open PR, unless the PR is a
draft. Once a PR is marked ready for review, its history must only move forward.

### Actions

When adding a GitHub Actions action, use the same version already used by other
jobs in the workflow files if it exists. Only when introducing an action not yet
used anywhere should you look up and use its latest stable release.

## Docs

Project documentation lives in the `docs/` directory. Read the relevant docs
before starting work. When a change makes any doc inaccurate (a feature is
added, removed, or significantly changed, or a decision is revised), update the
doc in the same change.

Docs are the specification: goals, requirements, concepts, and design. Each of
these should have exactly one definition. Do not redefine it elsewhere in the
docs; link to the existing definition instead.

`README.md` is a high-level introduction to the project and should not contain
in-depth detail.

## Docs Style

All Markdown section headers and table headers must use title case.

## Code Style

All exported symbols must have a full TSDoc comment describing what the function
does, its parameters (`@param`), and its return value (`@returns`). One-line
summaries are not sufficient for exported API. Symbols exported only so that
tests can access them must be marked `@internal` and are exempt from this rule.

For optional values, prefer `?` shorthand (`field?: T`, `param?: T`) over
explicit `| undefined` unions.
