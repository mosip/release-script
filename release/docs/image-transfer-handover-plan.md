# Image Transfer Handover Plan

## Goal

Hand over stage-to-stage Docker image transfer (`mosipdev → mosipdev2`, `mosipdev2 → mosipqa`, and similar paths) from DevOps to owning teams (Dev, QA), while keeping every transfer **authorized, audited, and hard to misuse**.

This plan builds on the existing Vidivi tool and the [Manual workflow to transfer images](https://github.com/mosip/release-script/actions/workflows/image-transfer.yml). It does **not** remove DevOps ownership of production (`mosipid` / `mosipint`) or Security signing.

---

## Problem today

| Current state | Risk after naive handover |
|---|---|
| DevOps runs most transfers | Anyone with Actions access can overwrite tags |
| One workflow for all destinations | Wrong org / wrong tag / wrong version chaos |
| Secrets exist per org, but one shared workflow | Token selection mistakes; over-privilege |
| Ticket + PR practice is informal | Incomplete audit of who moved what and why |
| `mosipid` is admin-protected (via `kattu`) | Lower stages (`dev2`, `qa`) have weaker gates |

Without controls, handover creates: accidental overwrites, tag pollution, environment skew (QA testing wrong digests), blame ambiguity, and pressure to “just re-run” without review.

---

## Design principles

1. **Least privilege** — A person or bot gets push rights only to the destination org(s) they own.
2. **Separation of duties** — Requester ≠ Approver ≠ (for prod) Releaser / Signer.
3. **Allowed paths only** — Transfers must follow the documented lifecycle; arbitrary org-to-org is blocked.
4. **PR is the request; workflow is the execution** — Image list changes are reviewed before push.
5. **Every run is attributable** — Actor, ticket, images, digests, destination, result are recorded.
6. **Fail closed** — Missing approval, wrong path, or mismatched secret → no transfer.
7. **DevOps remains the break-glass owner** — Emergency and prod stays with Release/DevOps + Security.

---

## Image lifecycle (unchanged)

```
mosipdev → mosipdev2 → mosipqa → mosipid
                 ↘ mosipqa / mosipint → mosipid   (staged / patch path)
```

Parallel Inji path (if used): `injistackdev → injistackdev2 → injistackqa → injistack`.

| Org | Purpose | Post-handover owner |
|---|---|---|
| `mosipdev` | CI-built / early Dev | Dev (write via CI; not via transfer workflow) |
| `mosipdev2` | Pre-QA staging | Dev leads / designated Dev transfer operators |
| `mosipqa` | QA test images | QA leads / designated QA transfer operators |
| `mosipint` | Interim / patch holding | Release / DevOps (restricted) |
| `mosipid` | Community / production release | Release / DevOps + Security signing |

---

## Target operating model

### RACI (per stage)

| Activity | Dev | QA | Release / DevOps | Security |
|---|---|---|---|---|
| Build & push to `mosipdev` (CI) | **R** | C | C | I |
| Transfer `mosipdev → mosipdev2` | **R** | C | A (policy) | I |
| Transfer `mosipdev2 → mosipqa` | C | **R** | A (policy) | I |
| Transfer `mosipqa → mosipid` / `mosipint` | C | C | **R** | **A** (signing) |
| Image signing after prod transfer | I | I | C | **R** |
| Break-glass / emergency transfer | C | C | **R** | A |
| Audit & access reviews | C | C | **R** | C |

R = Responsible, A = Accountable, C = Consulted, I = Informed.

### Named roles (not whole teams)

Do **not** grant transfer rights to every Dev or QA engineer.

| Role | Who | Rights |
|---|---|---|
| **Dev Transfer Operator** | 2–4 named Dev engineers (rotate) | Propose + (after approval) run transfers **into `mosipdev2` only** |
| **Dev Transfer Approver** | Dev lead(s) / module owners | Approve PRs / Environment for `→ mosipdev2` |
| **QA Transfer Operator** | 2–4 named QA engineers | Propose + run transfers **into `mosipqa` only** |
| **QA Transfer Approver** | QA lead(s) | Approve PRs / Environment for `→ mosipqa` |
| **Release Operator** | Build & Release / DevOps | Transfers into `mosipid` / `mosipint`; break-glass |
| **Security Signer** | Security team | Signing ticket after prod images land |
| **Audit reviewer** | Someone **not** who ran the transfer | Spot-check reports / digests (already aligned with post-release checks SoD) |

---

## Allowed transfer matrix (hard rule)

Only these destination hops are allowed for non-DevOps operators:

| Source org (in `images.txt`) | Destination org | Who may execute | Approval required |
|---|---|---|---|
| `mosipdev` | `mosipdev2` | Dev Transfer Operator | Dev Approver |
| `mosipdev2` | `mosipqa` | QA Transfer Operator | QA Approver |
| `mosipqa` | `mosipid` | Release / DevOps (admin) | Release lead + Security signing |
| `mosipqa` / `mosipdev2` | `mosipint` | Release / DevOps (admin) | Release lead |
| Any → any other | — | **Blocked** | — |

Additional rules:

- Destination tag should match release/sprint convention (no free-form `latest` for MOSIP services unless explicitly allowed).
- Overwriting an existing tag in `mosipqa` / `mosipid` requires explicit approval comment (“overwrite intentional: reason”).
- Source image must exist; `check` mode must pass before `push`.
- Prefer digest verification (`hash`) when replacing a tag.

---

## Control layers (defense in depth)

Implement all layers. No single control is enough.

### 1. People & process

1. **Ticket required** — Jira/DSD ticket with: source org, dest org, version/tag, image list (or link to PR), reason, requester, target date.
2. **PR required** — Change `images.txt` (or a stage-specific list file) via PR. No direct push to protected branches.
3. **CODEOWNERS** — Stage-specific owners review image-list PRs.
4. **Runbook** — Operators follow a short checklist (below); free-form local `vidivi.py push` to shared orgs is discouraged / forbidden for operators without break-glass.

### 2. GitHub repository access

| Control | Recommendation |
|---|---|
| Who can run Actions | Restrict `workflow_dispatch` via GitHub Environments (not “all write collaborators”) |
| Branch protection | Require PR + approvals on the branch that holds image lists |
| CODEOWNERS | `/release/vidivi/images-dev2.txt` → Dev leads; `/release/vidivi/images-qa.txt` → QA leads |
| Admin list | Keep `mosipid` admin-only protection in `mosip/kattu` |

### 3. Split workflows by stage (recommended)

Replace “one mega-workflow anyone can aim at any org” with stage-scoped workflows:

| Workflow | Destination fixed to | Secret | Environment |
|---|---|---|---|
| `image-transfer-dev2.yml` | `mosipdev2` only | `MOSIPDEV2_DOCKER_TOKEN` | `transfer-dev2` |
| `image-transfer-qa.yml` | `mosipqa` only | `MOSIPQA_DOCKER_TOKEN` | `transfer-qa` |
| `image-transfer-prod.yml` | `mosipid` / `mosipint` | `MOSIPID_*` / `MOSIPINT_*` | `transfer-prod` (admins + required reviewers) |

Benefits:

- Operators cannot “accidentally” select `MOSIPID_DOCKER_TOKEN`.
- Environment **required reviewers** gate the run.
- Audit logs clearly show which stage workflow ran.

Keep the existing generic workflow for DevOps break-glass only, or remove it after migration.

### 4. GitHub Environments (approval gates)

For each environment (`transfer-dev2`, `transfer-qa`, `transfer-prod`):

- **Required reviewers**: Approver role only (not the same GitHub group as Operators if possible).
- **Deployment branches**: Limit to agreed branches (e.g. `master` / release branch).
- **Wait timer** (optional for QA/prod): short delay so Slack notice can be seen before run proceeds.
- **Secrets scoped to Environment** — move Docker tokens from repo secrets to Environment secrets so only that workflow environment can use them.

### 5. Registry credentials (strongest technical gate)

| Destination | Credential type | Scope | Who holds it |
|---|---|---|---|
| `mosipdev2` | Docker Hub PAT / Harbor robot | **Push only to `mosipdev2`** | Environment `transfer-dev2` |
| `mosipqa` | Separate token/robot | **Push only to `mosipqa`** | Environment `transfer-qa` |
| `mosipid` / `mosipint` | Separate tokens | Push to those orgs only | Environment `transfer-prod` + admin |

Rules:

- Never share personal Docker passwords; use org tokens / Harbor robots with minimal scope.
- Rotate tokens on operator offboarding and on a fixed schedule (e.g. quarterly).
- Disable write access for tokens used only for CI pull if any.
- Prefer **immutable tags** or digest pinning in deploy configs so a mistaken re-push is less damaging (longer-term).

### 6. Workflow / `kattu` enforcement

Extend reusable workflow protections beyond `mosipid`:

| Check | Behavior |
|---|---|
| Allowed destination list per workflow | Fail if input ≠ fixed dest org |
| Allowed source org prefix in `images.txt` | Fail if source not in allowlist for that hop |
| Actor allowlist (optional) | Fail if GitHub actor not in Operators team |
| Protected orgs | Keep admin-only for `mosipid` (and add `mosipint`) |
| Dry-run / check-first | Always run `check` (and optionally `hash`) before `push` |
| Block `custom` secret path for stage workflows | No custom secret on Dev/QA workflows |

### 7. Monitoring & audit

Every transfer must produce a durable record:

| Signal | Where | Purpose |
|---|---|---|
| Workflow run | GitHub Actions run history | Who triggered, inputs, success/fail |
| Environment approval | GitHub Environment deployment log | Who approved |
| PR + ticket link | PR description / commit | Why |
| `transfer_report.md` | Committed or uploaded as workflow artifact | What moved |
| Digests | Report / `hash` output | Prove exact bits |
| Slack | Channel per stage (not only DevOps) | Real-time awareness |
| Weekly digest | Automated summary of transfers | Spot unusual volume / overwrites |

**Minimum Slack payload:** actor, ticket/PR, source→dest, image count, success/fail, run URL.

**Retention:** Keep Actions logs and transfer reports for at least one release cycle (prefer longer for prod).

### 8. Verification & separation of duties

- After `→ mosipqa`, a **QA engineer who did not run the transfer** confirms sample digests / smoke pull.
- After `→ mosipid`, continue existing Security signing ticket + post-release checks by a non-releaser (`release/checks`).

---

## Standard operating procedure (SOP)

### A. Dev → Dev2 (`mosipdev → mosipdev2`)

1. Dev Transfer Operator opens / updates ticket: list of images + tags + reason.
2. Operator opens PR updating the Dev2 image list (e.g. `images-dev2.txt`).
3. Dev Approver reviews: correct sources, tags, no unintended overwrites.
4. PR merges.
5. Operator starts `image-transfer-dev2` workflow (branch with merged list).
6. Environment `transfer-dev2` requires Dev Approver approval.
7. Workflow runs `check` → `push`; publishes report + Slack to `#image-transfer-dev2` (or equivalent).
8. Operator links run URL + report back on the ticket; closes ticket.

### B. Dev2 → QA (`mosipdev2 → mosipqa`)

Same pattern with QA Operator / QA Approver / `image-transfer-qa` / `#image-transfer-qa`.

**Entry criteria for QA handoff:** Dev confirms images validated in Dev2; ticket references sprint/release; tag set matches what QA will deploy.

### C. QA → Prod (`mosipqa → mosipid`)

Unchanged ownership: Release/DevOps only, admin-protected org, Security signing ticket after transfer, post-release checks by independent party.

### D. Break-glass

1. Only Release/DevOps.
2. Ticket marked `break-glass` with incident link.
3. Use prod or break-glass workflow; dual acknowledgment in Slack.
4. Post-incident: rotate credentials if compromise suspected; write short RCA.

---

## Anti-chaos / anti-misuse rules

| Rule | Why |
|---|---|
| Named operators only (small set) | Avoid “everyone can push” |
| Approver ≠ Operator for the same run | SoD |
| Fixed destination per workflow | No org mix-ups |
| No local push with shared org tokens | Tokens stay in CI Environments |
| One ticket / one PR / one hop | Prevent mega-batches mixing stages |
| Ban silent overwrites | Require explicit approval text |
| Rate / batch expectations | Unusual large transfers need lead approval |
| Freeze windows | Optional: no QA transfers during freeze without Release approval |
| Offboarding checklist | Remove from GitHub team + rotate token same day |

---

## Implementation roadmap

### Phase 0 — Agree ownership (no code)

- Nominate Operators and Approvers for Dev and QA.
- Confirm Slack channels and ticket project/labels (`image-transfer-dev2`, `image-transfer-qa`).
- Document freeze/break-glass contacts.

### Phase 1 — Process without new workflows

- Enforce ticket + PR for all lower-stage transfers.
- Add CODEOWNERS on `release/vidivi/images.txt` (or split files).
- DevOps still executes until Phase 2; teams prepare lists themselves.
- Start Slack notification habit and ticket linkage.

### Phase 2 — Technical gates (recommended core)

- Split workflows: `dev2`, `qa`, `prod`.
- Create GitHub Environments with required reviewers + environment-scoped secrets.
- Move tokens off shared repo-secret usage where possible.
- Restrict Environment access to Operator GitHub teams.
- Tighten `kattu` allowlists (source org + destination org).
- Keep generic workflow admin-only or retire it.

### Phase 3 — Observability & hygiene

- Structured Slack notifications per stage.
- Archive transfer reports as artifacts + optional commit.
- Weekly transfer summary (Actions API or script).
- Token rotation calendar; access review every sprint or monthly.
- Optional: immutable tags / digest pinning in Helm values for QA/prod.

### Phase 4 — Continuous improvement

- Metrics: failed transfers, overwrite rate, time-to-approve, transfers without ticket.
- Periodic drill: revoke an operator; confirm they cannot approve or run.
- Align Inji / other org paths to the same model.

---

## Suggested GitHub team layout

| GitHub team | Members | Used for |
|---|---|---|
| `mosip-image-transfer-dev-ops` | Dev Operators | Can start `transfer-dev2` |
| `mosip-image-transfer-dev-approvers` | Dev Approvers | Environment reviewers for `transfer-dev2` |
| `mosip-image-transfer-qa-ops` | QA Operators | Can start `transfer-qa` |
| `mosip-image-transfer-qa-approvers` | QA Approvers | Environment reviewers for `transfer-qa` |
| `mosip-release-admins` | Release/DevOps | `transfer-prod` + break-glass |

Prefer **disjoint** ops vs approver teams so the same person is not always self-approving. If headcount is small, allow self-approve only for Dev2, never for QA→Prod; still keep a second person review on the PR.

---

## Checklist before declaring handover complete

- [ ] Operators and Approvers named and documented
- [ ] Stage workflows live with fixed destinations
- [ ] Environment required reviewers configured
- [ ] Tokens scoped per org and stored as Environment secrets
- [ ] CODEOWNERS / PR review on image lists
- [ ] Slack alerts working per stage
- [ ] SOP published; teams trained on one dry-run each
- [ ] `mosipid` / `mosipint` still admin-only; Security signing unchanged
- [ ] Break-glass procedure written and tested once
- [ ] Offboarding + token rotation procedure owned by DevOps
- [ ] First two real transfers audited end-to-end (ticket → PR → approve → run → report)

---

## What DevOps still owns after handover

- Production / interim transfers (`mosipid`, `mosipint`)
- Reusable workflow protections in `mosip/kattu`
- Registry org policy, token issuance/rotation
- Break-glass execution
- Access reviews and audit tooling
- Platform changes to Vidivi / Actions

Dev and QA own **their hop only**: preparing the image list, getting approval, triggering the stage workflow, and confirming the result for that stage.

---

## Summary

Hand over **authority by stage**, not the whole transfer button. Combine **named operators**, **mandatory ticket+PR**, **stage-specific workflows**, **GitHub Environment approvals**, **org-scoped registry tokens**, and **Slack/report audit**. Keep **prod and signing** with Release/DevOps + Security. That is the clean path to remove DevOps from day-to-day `dev→dev2` and `dev2→qa` moves without inviting misuse or chaos.
