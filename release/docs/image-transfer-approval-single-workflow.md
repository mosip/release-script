# Approval-based image transfer — single workflow (not multiple YAMLs)

## Short answer

You **do not need** one workflow file per hop (`*-dev2.yml`, `*-qa.yml`, …).

Use **one** workflow (`image-transfer.yml`) and select a **TRANSFER_TARGET**. That value is the GitHub Environment name. GitHub then:

1. Pauses the job for that Environment’s **required reviewers**
2. After Approve, unlocks that Environment’s **DOCKER_TOKEN**
3. Pushes only to the **destination org mapped from that target**

Multiple YAMLs were only one optional design. **One YAML + multiple Environments** is enough and matches how you work today (one Actions entry point).

---

## What changes are needed

### A. GitHub UI (must do — cannot be done by YAML alone)

Create these Environments under `mosip/release-script` → **Settings** → **Environments**:

| Environment name (`TRANSFER_TARGET`) | Required reviewers | Environment secret | Pushes to |
|---|---|---|---|
| `transfer-dev2` | Dev approvers | `DOCKER_TOKEN` = mosipdev2 token | `mosipdev2` |
| `transfer-qa` | QA approvers | `DOCKER_TOKEN` = mosipqa token | `mosipqa` |
| `transfer-mosipint` | Release / DevOps | `DOCKER_TOKEN` = mosipint token | `mosipint` |
| `transfer-mosipid` | Release admins | `DOCKER_TOKEN` = mosipid token | `mosipid` |
| `transfer-injistack-dev2` | Inji/Dev approvers | `DOCKER_TOKEN` = injistackdev2 token | `injistackdev2` |
| `transfer-injistack-qa` | Inji/QA approvers | `DOCKER_TOKEN` = injistackqa token | `injistackqa` |
| `transfer-injistack` | Release | `DOCKER_TOKEN` = injistack token | `injistack` |

On each Environment:

1. **Required reviewers** (users/teams; max 6; any one approval is enough)
2. **Prevent self-review**
3. Optional: wait timer, allowed branches (`release-1.2.0.1` / `master`)
4. Secret name must be exactly **`DOCKER_TOKEN`** on every Environment (values differ)

Then **remove or stop using** the old repo-level org tokens for routine runs (`MOSIPDEV2_DOCKER_TOKEN`, etc.) so nothing can bypass the gate. Keep `SLACK_WEBHOOK_DEVOPS` and `WIREGUARD_CONFIG` as repository secrets.

### B. Workflow YAML (already the single-file model)

File: `.github/workflows/image-transfer.yml`

| Before (today’s misuse risk) | After (approval-based, one file) |
|---|---|
| Free `DESTINATION_ORGANIZATION` text | Derived from `TRANSFER_TARGET` |
| Free `SECRET_NAME` choice | Fixed Environment secret `DOCKER_TOKEN` |
| Job starts immediately | `environment: ${{ inputs.TRANSFER_TARGET }}` → waits for Approve |
| One workflow, weak binding | One workflow, strong binding via Environments |

Flow inside the YAML:

```
resolve-target  →  map TRANSFER_TARGET → DESTINATION_ORGANIZATION
       ↓
Image-transfer  →  environment: TRANSFER_TARGET (approval gate)
                →  secrets.DOCKER_TOKEN (unlocked after Approve)
                →  calls mosip/kattu image-transfer reusable workflow
```

### C. Process (unchanged ritual, plus Approve)

1. Ticket + PR updating `release/vidivi/images.txt` (same as KT)
2. Merge PR
3. **Run workflow** → pick `TRANSFER_TARGET` (e.g. `transfer-qa`) + username/registry
4. Job **Waiting** → Approver **Review deployments** → Approve / Reject
5. Transfer runs → verify tags → close ticket

### D. No change required in `kattu` for basic gating

`environment:` on the **caller** job is enough for Approve + Environment secrets. Existing `mosipid` admin protection in `kattu` remains an extra layer.

Optional later in `kattu`: allowlist source org prefixes per destination.

---

## Why one YAML is enough

| Concern | How one YAML handles it |
|---|---|
| Different approvers per hop | Different Environment configs (reviewers), same workflow file |
| Different tokens per hop | Same secret **name** `DOCKER_TOKEN`, different **value** per Environment |
| Operator picks wrong org | Org is **mapped** from `TRANSFER_TARGET`; not free text |
| Audit | Each Environment has its own deployment history |
| Same UX as today | Still one Actions workflow to click |

You only need multiple YAML files if you want **separate Actions menu entries** (harder to mis-click target). That is optional UX, not a security requirement.

---

## Mapping reference (encoded in the workflow)

| `TRANSFER_TARGET` | Destination org |
|---|---|
| `transfer-dev2` | `mosipdev2` |
| `transfer-qa` | `mosipqa` |
| `transfer-mosipint` | `mosipint` |
| `transfer-mosipid` | `mosipid` |
| `transfer-injistack-dev2` | `injistackdev2` |
| `transfer-injistack-qa` | `injistackqa` |
| `transfer-injistack` | `injistack` |

To add a new hop later: add a choice option + one `case` arm + create the matching GitHub Environment with `DOCKER_TOKEN`.

---

## Operator vs Approver access (reminder)

| Role | Repo access | Also need |
|---|---|---|
| Operator (PR + Run workflow) | **Write** | — |
| Approver (Approve deployment) | **Read** minimum | Listed on that Environment’s required reviewers |
| Merger / Release lead | **Write** or **Maintain** | Allowed to merge by branch protection / CODEOWNERS |
| Admin (Environments / secrets) | **Admin** | — |

### Does Write also allow merging PRs?

**Only if the branch is unprotected.** Write includes the *capability* to merge, but **branch protection / rulesets** can block it.

Give operators **Write** so they can:

- Push a feature branch  
- Open a PR  
- Run `workflow_dispatch`

Then lock merges with protection on `release-1.2.0.1` (and other release branches):

| Setting | Purpose |
|---|---|
| Require a pull request before merging | No direct pushes to the release branch |
| Require approvals (1+) | Someone else must approve the PR |
| Require review from Code Owners | e.g. DevOps / leads own `release/vidivi/images.txt` |
| Do not allow bypassing the above settings | Admins cannot casually skip (or limit bypass actors) |
| Restrict who can push to matching branches | Only named Release/DevOps users if you want a hard merge gate |
| (Optional) Require conversation resolution | Forces comment cleanup before merge |

With that:

| Action | Operator (Write) | Approver (Read + env reviewer) | Release lead / CODEOWNER |
|---|---|---|---|
| Open PR / update `images.txt` | Yes | Optional | Yes |
| Run transfer workflow | Yes | No (Read cannot `workflow_dispatch`) | Yes |
| Approve Environment wait | No (unless also listed; block with prevent self-review) | Yes | If listed |
| Merge PR | **No** (blocked until required reviews) | Can approve PR if Write/CODEOWNER | **Yes** after review |

So: **Write ≠ automatic merge rights** once branch protection is on. That is the standard GitHub pattern worldwide.

**Practical setup:** Operators team = Write; Approvers for Environment = Read (or Write if they also review PRs); CODEOWNERS / “restrict who can merge” = Release/DevOps leads only.

---

## Rollout checklist

- [ ] Create Environments listed above with reviewers + prevent self-review
- [ ] Add `DOCKER_TOKEN` on each Environment (correct org push token)
- [ ] Merge updated single `image-transfer.yml`
- [ ] Test `transfer-dev2` with a small `images.txt` batch (Approve path)
- [ ] Test Reject path once
- [ ] Test prevent self-review (operator cannot approve own run)
- [ ] Remove old repo-level Docker org tokens used by the previous free-form inputs
- [ ] Train operators: pick **TRANSFER_TARGET**, not a free destination string

---

## Related docs

- [Image Transfer KT (as-is process)](./image-transfer-kt.md)
- [Handover plan](./image-transfer-handover-plan.md)
- [GitHub Environments deep dive](./github-environments-image-transfer.md)
- [Vidivi README](../vidivi/README.md)
