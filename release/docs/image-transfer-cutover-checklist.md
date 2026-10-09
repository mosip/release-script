# Switch to approval-based image transfer — cutover checklist

Use this when you are ready to **go live**.  
Code for the single approval workflow is already on branch `cursor/image-transfer-handover-plan-9728` (PR).  
Most remaining work is **GitHub UI + people + branch protection**, not more YAML.

---

## Already done in the PR (code/docs)

| Item | Status |
|---|---|
| Single workflow `.github/workflows/image-transfer.yml` with `TRANSFER_TARGET` | Done |
| Destination org derived from target (no free-typed org) | Done |
| `environment: ${{ inputs.TRANSFER_TARGET }}` approval gate | Done |
| Uses Environment secret `DOCKER_TOKEN` | Done |
| Per-hop YAML files removed (not needed) | Done |
| KT / handover / Environments docs | Done |
| Vidivi README updated for new inputs | Done |

**Do not merge this workflow to the default release branch until Steps 1–3 below are ready**, or the first run will fail / run without a real gate.

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

### Step 5 — Merge the approval workflow PR

1. Review and merge PR `#1786` (or current PR) into the release branch you use for transfers  
2. Confirm Actions shows **Manual workflow to transfer images** with input **`TRANSFER_TARGET`** (no free `DESTINATION_ORGANIZATION` / `SECRET_NAME`)

---

### Step 6 — Pilot test (before announcing to all teams)

Use a tiny `images.txt` PR + real Environments:

1. Operator opens PR → CODEOWNER merges  
2. Operator runs workflow: `TRANSFER_TARGET=transfer-dev2`  
3. Confirm job is **Waiting**  
4. Approver (not operator) **Review deployments** → Approve  
5. Confirm transfer succeeds  
6. Repeat once with **Reject**  
7. Confirm operator cannot approve own run (prevent self-review)  
8. Optional: same pilot for `transfer-qa`

Only after pilot passes → announce cutover.

---

### Step 7 — Remove bypass paths (critical)

After pilot success:

- [ ] Delete or empty **repository** secrets: `MOSIPDEV2_DOCKER_TOKEN`, `MOSIPQA_DOCKER_TOKEN`, `MOSIPID_DOCKER_TOKEN`, `MOSIPINT_DOCKER_TOKEN`, `INJISTACK_DOCKER_TOKEN` (and any custom org tokens used only by the old form)  
- [ ] Confirm no other workflow still needs those repo secrets  
- [ ] Document break-glass: only admins can edit Environment reviewers / secrets  

If old repo tokens remain, someone could add another unprotected workflow and bypass the gate.

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
