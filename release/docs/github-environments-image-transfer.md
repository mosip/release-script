# GitHub Environments for Image Transfer — What They Are & How to Implement

## What is a GitHub Environment?

A **GitHub Environment** is a named deployment target in a repository (for example `transfer-dev2`, `transfer-qa`, `transfer-prod`). It is **not** a server and **not** Docker Hub. It is a **control gate** inside GitHub Actions.

When a workflow job declares:

```yaml
jobs:
  transfer:
    environment: transfer-dev2
```

GitHub does three important things **before that job can run or read environment secrets**:

1. Applies **protection rules** (required reviewers, wait timer, allowed branches).
2. Creates a **deployment record** (who triggered, who approved, when, which commit).
3. Unlocks **Environment secrets** only for that job (and only after rules pass).

### Why this matters for image transfer

Today, anyone who can run the manual image-transfer workflow can aim it at any org (if they pick the right secret). With Environments:

| Without Environments | With Environments |
|---|---|
| Click **Run workflow** → job starts immediately | Click **Run workflow** → job waits for Approver |
| Repo secrets readable by any write-access workflow | Docker push token locked in Environment; released only after approval |
| Weak audit of “who allowed this” | Approver name stored on the deployment |
| One workflow can target any destination | Stage workflow + fixed Environment = fixed destination |

```
Operator clicks "Run workflow"
        │
        ▼
Job references environment: transfer-qa
        │
        ▼
GitHub pauses job  ──►  Slack/email to Required Reviewers
        │
        ▼
QA Approver clicks Approve (or Reject)
        │
        ▼
Environment secrets unlocked (e.g. MOSIPQA_DOCKER_TOKEN)
        │
        ▼
Reusable kattu image-transfer job runs
        │
        ▼
Deployment history + Actions log = audit trail
```

### Requirements / limits to know

- **Required reviewers** and **environment secrets** on private repos need GitHub Team / Enterprise (public repos: available on Free). MOSIP public repos can use this; confirm plan if the repo is private/internal.
- Up to **6** required reviewers (users or teams). **Any one** approval is enough (not majority).
- Enable **Prevent self-review** so the person who started the run cannot approve it.
- Unapproved jobs fail after **30 days**.
- Environment secrets are only visible to jobs that set `environment: <name>`.

---

## Target setup for MOSIP image transfer

| Environment name | Used by workflow | Required reviewers | Environment secret(s) | Fixed destination org |
|---|---|---|---|---|
| `transfer-dev2` | `image-transfer-dev2.yml` | Dev Approver team | `MOSIPDEV2_DOCKER_TOKEN` | `mosipdev2` |
| `transfer-qa` | `image-transfer-qa.yml` | QA Approver team | `MOSIPQA_DOCKER_TOKEN` | `mosipqa` |
| `transfer-prod` | `image-transfer-prod.yml` | Release admins | `MOSIPID_DOCKER_TOKEN`, `MOSIPINT_DOCKER_TOKEN` | `mosipid` / `mosipint` |

Repo-level secrets that can stay shared (not stage-specific): `SLACK_WEBHOOK_DEVOPS`, `WIREGUARD_CONFIG`.

---

## Full implementation steps

### Phase A — Prepare people (Day 0)

#### Step A1. Nominate roles

| Role | Example | Count |
|---|---|---|
| Dev Transfer Operators | Engineers who prepare PRs and click Run | 2–4 |
| Dev Transfer Approvers | Dev leads who approve Environment waits | 1–3 |
| QA Transfer Operators | QA engineers | 2–4 |
| QA Transfer Approvers | QA leads | 1–3 |
| Release admins | DevOps / Release | existing |

Approvers and Operators should be **different people** when possible.

#### Step A2. Create GitHub teams (org settings)

Path: GitHub **Organization** → **Teams** → **New team**

Create:

1. `mosip-image-transfer-dev-ops`
2. `mosip-image-transfer-dev-approvers`
3. `mosip-image-transfer-qa-ops`
4. `mosip-image-transfer-qa-approvers`
5. `mosip-release-admins` (if not already present)

Add the named people to each team.

#### Step A3. Grant repo access

Path: `mosip/release-script` → **Settings** → **Collaborators and teams**

- Give Operator teams **Write** (needed to run `workflow_dispatch`).
- Approver teams need at least **Read** (GitHub allows Environment approval with read); Write is fine if they already have it.
- Do **not** put all of Dev/QA on Write just for this — only named operators.

---

### Phase B — Create Environments in the repo (UI)

Path: `mosip/release-script` → **Settings** → **Environments** → **New environment**

Repeat for `transfer-dev2`, `transfer-qa`, `transfer-prod`.

#### Step B1. Create environment `transfer-dev2`

1. Name: `transfer-dev2`
2. Click **Configure environment**.

#### Step B2. Protection rules

1. Check **Required reviewers**.
2. Add team: `mosip-image-transfer-dev-approvers` (or individual leads).
3. Check **Prevent self-review**.
4. Optional: **Wait timer** = `1`–`5` minutes (gives Slack time to notify).
5. Optional: **Deployment branches** → Selected branches → allow only `master` / `main` / your release branch (stops runs from random forks/branches).
6. Click **Save protection rules**.

#### Step B3. Environment secret

1. Under **Environment secrets** → **Add environment secret**.
2. Name: `MOSIPDEV2_DOCKER_TOKEN`
3. Value: Docker Hub / Harbor token that can **push only to `mosipdev2`**.
4. Save.

#### Step B4. Repeat for QA and Prod

| Environment | Reviewers | Prevent self-review | Secrets |
|---|---|---|---|
| `transfer-qa` | `mosip-image-transfer-qa-approvers` | Yes | `MOSIPQA_DOCKER_TOKEN` |
| `transfer-prod` | `mosip-release-admins` | Yes | `MOSIPID_DOCKER_TOKEN`, `MOSIPINT_DOCKER_TOKEN` |

#### Step B5. Move tokens off repo secrets (important)

After Environment secrets work in a test run:

1. Settings → **Secrets and variables** → **Actions** (repository secrets).
2. Remove or rotate the old repo-level `MOSIPDEV2_DOCKER_TOKEN` / `MOSIPQA_DOCKER_TOKEN` so they are **not** usable by unprotected workflows.
3. Keep `SLACK_WEBHOOK_DEVOPS` and `WIREGUARD_CONFIG` as repository secrets if all workflows need them.

Until you remove repo copies, a workflow **without** an Environment can still use the old repo secret — that defeats the gate.

---

### Phase C — Add stage workflows (code)

Add separate workflows so destination cannot be mistyped.

#### Example: Dev2 workflow

File: `.github/workflows/image-transfer-dev2.yml`

```yaml
name: Transfer images to mosipdev2

on:
  workflow_dispatch:
    inputs:
      USERNAME:
        description: 'Registry username (Docker Hub user or Harbor robot)'
        required: true
        type: string
      REGISTRY_URL:
        description: 'Destination registry URL'
        required: true
        default: 'https://index.docker.io/v1/'
        type: string
      REGISTRY_TYPE:
        description: 'Destination registry type'
        required: true
        default: 'dockerhub'
        type: choice
        options:
          - dockerhub
          - harbor
          - other
      ENABLE_WIREGUARD:
        description: 'Enable WireGuard VPN for private Harbor'
        required: false
        default: false
        type: boolean

jobs:
  # Gate: waits for Environment approval; unlocks Environment secrets
  Image-transfer:
    environment: transfer-dev2
    uses: mosip/kattu/.github/workflows/image-transfer.yml@master
    with:
      DESTINATION_ORGANIZATION: mosipdev2   # FIXED — operators cannot change this
      REGISTRY_URL: ${{ inputs.REGISTRY_URL }}
      REGISTRY_TYPE: ${{ inputs.REGISTRY_TYPE }}
      ENABLE_WIREGUARD: ${{ inputs.ENABLE_WIREGUARD }}
      USERNAME: ${{ inputs.USERNAME }}
    secrets:
      # From Environment secret (available only after approval)
      TOKEN: ${{ secrets.MOSIPDEV2_DOCKER_TOKEN }}
      # From repository secrets
      SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_DEVOPS }}
      WIREGUARD_CONFIG: ${{ secrets.WIREGUARD_CONFIG }}
```

#### Example: QA workflow

File: `.github/workflows/image-transfer-qa.yml`

Same shape, but:

- `environment: transfer-qa`
- `DESTINATION_ORGANIZATION: mosipqa`
- `TOKEN: ${{ secrets.MOSIPQA_DOCKER_TOKEN }}`

#### Example: Prod workflow (DevOps only)

- `environment: transfer-prod`
- Input choice limited to `mosipid` / `mosipint` only
- Tokens from prod Environment secrets
- Optionally restrict who can see/run it via repo permissions + admin-only kattu protection

#### What to do with the old generic workflow

| Option | Recommendation |
|---|---|
| A. Restrict to admins / leave as break-glass | Short term OK |
| B. Delete after stage workflows are proven | Preferred long term |
| C. Point it at `transfer-prod` only | If you still need one flexible entry for Release |

Do **not** leave the old workflow able to read Dev2/QA tokens from repository secrets.

---

### Phase D — Image list process (PR gate)

Environments gate **execution**. PRs gate **what** gets transferred.

1. Operator updates `release/vidivi/images.txt` (or split files `images-dev2.txt` / `images-qa.txt`) via PR.
2. Approver reviews image list + ticket link.
3. Merge PR.
4. Operator runs the stage workflow on the branch that contains the merged list.
5. Environment Approver approves the waiting deployment.

Optional CODEOWNERS:

```
# .github/CODEOWNERS
/release/vidivi/images-dev2.txt  @mosip/mosip-image-transfer-dev-approvers
/release/vidivi/images-qa.txt    @mosip/mosip-image-transfer-qa-approvers
```

---

### Phase E — Operator & Approver runbook

#### Operator (start transfer)

1. Ensure PR with image list is merged and ticket is open.
2. Go to **Actions** → **Transfer images to mosipdev2** (or QA).
3. **Run workflow** → fill username / registry → Run.
4. Job shows status **Waiting** (yellow) for Environment approval.
5. Notify Approver (Slack) with Actions run URL + ticket.
6. After approval, wait for success; attach `transfer_report` / run URL on ticket.

#### Approver (approve or reject)

1. Open the Actions run URL (or repo **Deployments**).
2. Review: actor, branch, destination Environment, linked ticket/PR.
3. Click **Review deployments** → select Environment → **Approve** or **Reject**.
4. If something looks wrong (wrong branch, no ticket, unexpected overwrite): **Reject** and comment on ticket.

Screenshot path in UI:

`Actions` → select run → banner **Review deployments** → choose environment → Approve / Reject.

---

### Phase F — Verification checklist (do this once before handover)

- [ ] Create Environments with required reviewers + prevent self-review.
- [ ] Put Docker tokens only in Environment secrets; remove from repo secrets.
- [ ] Merge stage workflow files (`*-dev2`, `*-qa`, `*-prod`).
- [ ] Test Dev2: Operator starts run → job waits → Approver approves → transfer succeeds.
- [ ] Test self-review blocked: Operator who started run cannot approve.
- [ ] Test reject path: Approver rejects → job does not transfer.
- [ ] Confirm old generic workflow cannot push to Dev2/QA (token gone or workflow restricted).
- [ ] Confirm Slack still notifies.
- [ ] Confirm Deployment history shows actor + approver.
- [ ] Train both teams with one dry-run each.

---

## How secrets resolve (important detail)

```yaml
secrets:
  TOKEN: ${{ secrets.MOSIPDEV2_DOCKER_TOKEN }}
```

Lookup order for a job with `environment: transfer-dev2`:

1. Environment secret `MOSIPDEV2_DOCKER_TOKEN` on `transfer-dev2` (preferred).
2. Else repository / org secret with the same name (fallback — avoid leaving these).

Only jobs that declare that Environment get Environment secrets, and only **after** protection rules pass. That is the core security property.

---

## Mapping to reusable workflow (`mosip/kattu`)

Your caller already does:

```yaml
uses: mosip/kattu/.github/workflows/image-transfer.yml@master
```

Putting `environment:` on that **caller** job is enough:

- GitHub waits for approval **before** starting the reusable workflow.
- Caller can pass Environment secrets into `secrets: TOKEN: ...`.
- Existing `mosipid` admin protection inside `kattu` remains an extra layer for prod.

No change is required inside `kattu` for basic Environment gating. Optional later: add source-org allowlists inside `kattu` for defense in depth.

---

## Minimal vs full adoption

| Level | What you do | Protection gained |
|---|---|---|
| **Minimal** | One Environment on existing workflow + required reviewers | Human approval before any transfer |
| **Recommended** | Stage Environments + stage workflows + Environment secrets | Approval + least-privilege tokens + fixed destination |
| **Full** | Above + CODEOWNERS + ticket SOP + remove generic workflow + weekly access review | Process + technical + audit hygiene |

Start with **Recommended** for `transfer-dev2` and `transfer-qa`; keep prod on `transfer-prod` with Release only.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Job never waits for approval | Job missing `environment:` | Add `environment: transfer-dev2` on the transfer job |
| `TOKEN` empty / unauthorized | Secret still only on repo, or wrong name; or job has no environment | Add Environment secret; ensure job references that Environment |
| Operator can approve own run | Prevent self-review off | Enable on Environment |
| Approver cannot see Approve button | Not in required reviewers / no repo access | Add to reviewer team; grant Read+ |
| Wrong images transferred | `images.txt` not reviewed | Enforce PR + CODEOWNERS before run |
| Old workflow still pushes | Repo secret still present | Delete/rotate repo secret |

---

## Related docs

- [Image Transfer Handover Plan](./image-transfer-handover-plan.md)
- [Test approval on WireGuard onboard/offboard (recommended first)](./wg-lifecycle-approval-test.md)
- [Vidivi README](../vidivi/README.md)
- GitHub docs: [Managing environments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments)
- GitHub docs: [Reviewing deployments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/review-deployments)
