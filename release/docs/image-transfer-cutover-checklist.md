# Switch to approval-based image transfer — cutover checklist

Use this when you are ready to **go live** with approvals.  
**Merging this PR does not switch production** — `image-transfer.yml` stays the current (as-is) workflow.

Approval path: `.github/workflows/image-transfer-with-approval.yml`  
(Valid pattern: separate `approve` job with `environment:`; then call `kattu`. Existing `MOSIP*_DOCKER_TOKEN` repo secrets are reused.)

**Before changing MOSIP operations:** practice Approve/Reject in your fork — see [Sandbox test guide](./image-transfer-sandbox-test.md).

---

## Already done in the PR (code/docs)

| Item | Status |
|---|---|
| Production `image-transfer.yml` unchanged in behavior | Done (safe to merge) |
| Optional `image-transfer-with-approval.yml` (gate job + mapped existing secrets) | Done |
| Sandbox workflow for fork testing | Done |
| KT / handover / Environments / cutover docs | Done |
| CODEOWNERS stub (commented) | Done |

**Do not tell operators to use the approval workflow until Steps 1–3 (Environments + people) are ready.**

---

## What still must change (in order)

### Step 1 — People (DevOps lead, 30 min)

Nominate and write down:

| Role | Names / GitHub team | Count |
|---|---|---|
| Dev2 operators | | 2–4 |
| Dev2 Environment approvers | | 1–3 (≠ operators) |
| QA operators | | 2–4 |
| QA Environment approvers | | 1–3 |
| Prod / int operators + approvers | Release / DevOps only | small |
| Who may **merge** `images.txt` PRs | Release leads / CODEOWNERS | small |

Create GitHub org teams if useful (optional but cleaner):

- `mosip-image-transfer-dev-ops`
- `mosip-image-transfer-dev-approvers`
- `mosip-image-transfer-qa-ops`
- `mosip-image-transfer-qa-approvers`
- `mosip-release-admins`

Grant on `mosip/release-script`:

| Team | Repo role |
|---|---|
| Operators | **Write** |
| Environment approvers | **Read** (or Write if they also review PRs) |
| Release / merge owners | **Maintain** or Write + listed on branch protection |

---

### Step 2 — Create GitHub Environments (repo Admin, required)

Path: `mosip/release-script` → **Settings** → **Environments** → **New environment**

Create each name **exactly**:

| Environment | Reviewers | Prevent self-review | Environment secret |
|---|---|---|---|
| `transfer-dev2` | Dev2 approvers | Yes | `DOCKER_TOKEN` = push token for **mosipdev2** |
| `transfer-qa` | QA approvers | Yes | `DOCKER_TOKEN` = push token for **mosipqa** |
| `transfer-mosipint` | Release | Yes | `DOCKER_TOKEN` = **mosipint** |
| `transfer-mosipid` | Release admins | Yes | `DOCKER_TOKEN` = **mosipid** |
| `transfer-injistack-dev2` | Inji/Dev approvers | Yes | `DOCKER_TOKEN` = **injistackdev2** |
| `transfer-injistack-qa` | Inji/QA approvers | Yes | `DOCKER_TOKEN` = **injistackqa** |
| `transfer-injistack` | Release | Yes | `DOCKER_TOKEN` = **injistack** |

Per Environment also set (recommended):

- Deployment branches: only `release-1.2.0.1` / `master` (whatever you actually run from)
- Optional wait timer: 1–2 minutes

**Secret name must be exactly `DOCKER_TOKEN` on every Environment.** Values differ.

Keep as **repository** secrets (unchanged):

- `SLACK_WEBHOOK_DEVOPS`
- `WIREGUARD_CONFIG`

---

### Step 3 — Branch protection so Write ≠ merge (repo Admin)

On release branches (e.g. `release-1.2.0.1`):

- [ ] Require pull request before merging  
- [ ] Require at least 1 approval  
- [ ] Require review from Code Owners (after Step 4)  
- [ ] Do not allow bypassing (or limit bypass to admins only)  
- [ ] Restrict who can push / merge to Release leads if you want a hard gate  

Operators keep **Write** (PR + Run workflow) but cannot merge alone.

---

### Step 4 — CODEOWNERS for `images.txt` (code, small change)

Add `.github/CODEOWNERS` so image-list PRs need the right review, for example:

```
# Image transfer manifest — Release / DevOps review before merge
/release/vidivi/images.txt  @mosip/mosip-release-admins
```

Adjust the team/user to whatever exists in the MOSIP org.  
Enable **Require review from Code Owners** on the branch rule after this file is merged.

---

### Step 5 — Merge the docs/PR (safe anytime)

1. Merge PR `#1786` — production `image-transfer.yml` keeps working as today  
2. Confirm Actions still has **Manual workflow to transfer images** (old inputs)  
3. Confirm optional **Manual workflow to transfer images (with approval)** is visible but unused until pilot  

---

### Step 6 — Pilot the approval workflow (before announcing)

Use a tiny `images.txt` PR + real Environments:

1. Operator opens PR → reviewer merges  
2. Operator runs **with approval** workflow: `TRANSFER_TARGET=transfer-dev2`  
3. Confirm job `approve` is **Waiting**  
4. Approver (not operator) **Review deployments** → Approve  
5. Confirm transfer succeeds (uses existing `MOSIPDEV2_DOCKER_TOKEN`)  
6. Repeat once with **Reject**  
7. Confirm prevent self-review  
8. Optional: same pilot for `transfer-qa`

Only after pilot passes → tell teams to use the approval workflow (or retire the old one).

---

### Step 7 — Retire the old free-form workflow (after pilot)

After pilot success:

- [ ] Point operators to **with approval** workflow only  
- [ ] Optionally disable/remove free-form destination inputs by archiving old `image-transfer.yml` usage (or restrict who can run it)  
- [ ] Keep `MOSIP*_DOCKER_TOKEN` repo secrets until Approach A (Environment secrets via `kattu`) is implemented  
- [ ] Document break-glass: only admins can edit Environment reviewers  

Do **not** delete repo Docker tokens while `image-transfer-with-approval.yml` still maps to them.

---

### Step 8 — Process update for teams

Share the new runbook (short):

1. Ticket (`DSD-…`)  
2. PR updating `release/vidivi/images.txt` only  
3. Wait for CODEOWNER / lead merge  
4. Actions → Manual image transfer → choose **`TRANSFER_TARGET`** + username/registry  
5. Approver Approves Environment wait  
6. Verify destination tags → close ticket  
7. For `transfer-mosipid`: Security signing ticket (unchanged)

Point them to:

- [Image Transfer KT](./image-transfer-kt.md) (as-is ritual + PR examples)  
- [Single approval workflow](./image-transfer-approval-single-workflow.md) (new inputs)  

---

## What does *not* need changing

| Area | Why |
|---|---|
| `release/vidivi/vidivi.py` | Still used via `kattu`; no change required for gating |
| `images.txt` format | Same `source:tag dest-tag` lines |
| Ticket + PR habit | Same; approval is an *extra* gate on the run |
| `mosip/kattu` reusable workflow | Caller Environment gate is enough; `mosipid` admin rule stays |
| Slack / WireGuard repo secrets | Stay at repo level |

Optional later (not required for switch):

- Source-org allowlist inside `kattu`  
- Immutable tags / digest pinning in Helm  
- WG onboard `wg-lifecycle` Environment (separate practice)

---

## Cutover day one-pager

```
BEFORE merge:
  [ ] People named
  [ ] Environments created + DOCKER_TOKEN set
  [ ] Branch protection + CODEOWNERS ready

MERGE:
  [ ] Merge approval-based image-transfer.yml

SAME DAY:
  [ ] Pilot Approve on transfer-dev2
  [ ] Pilot Reject once
  [ ] Remove old repo Docker tokens
  [ ] Announce new TRANSFER_TARGET runbook
```

---

## Rollback

If something breaks after merge:

1. Re-add temporary **repository** secret `DOCKER_TOKEN` is **not** enough for all targets — prefer restoring previous workflow from git and/or putting tokens back as repo secrets only as emergency  
2. Proper rollback: revert the workflow commit to the old `SECRET_NAME` + `DESTINATION_ORGANIZATION` form  
3. Keep Environments in place; they do not hurt the old workflow  

---

## Owner map for the switch

| Workstream | Owner |
|---|---|
| Environments + secrets | Repo Admin / DevOps |
| Teams + Write/Read roles | Org Admin / DevOps |
| Branch protection + CODEOWNERS | Repo Admin |
| Merge workflow PR | Release lead |
| Pilot transfers | One Dev operator + one Approver |
| Announce / KT | DevOps |

When Step 1–3 are done in the GitHub UI, say so and we can add the `CODEOWNERS` file and help with the pilot run checklist against the live Environments.
