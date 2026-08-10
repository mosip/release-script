# Test GitHub Environment approval on WireGuard onboard/offboard

Use the rapid-deployment **WireGuard onboard/offboard** workflow in
[`mosip/infra`](https://github.com/mosip/infra/blob/master/.github/workflows/wg-onboard.yml)
as the first place to try Approve / Reject — before rolling the same pattern
to image transfer.

## Important design rule

Do **not** set:

```yaml
environment: ${{ inputs.ENV_NAME }}
```

That input is the **target** Environment this workflow creates (Helmsman secrets
`TF_WG_CONFIG`, `CLUSTER_WIREGUARD_WG0`, `CLUSTER_WIREGUARD_WG1`). On first
onboard it often does not exist yet, so it cannot be the approval gate.

Use a **fixed gate** Environment instead:

```yaml
jobs:
  onboard:
    environment: wg-lifecycle   # approval gate (fixed name)
```

| Name | Role |
|---|---|
| `wg-lifecycle` | Who must Approve before the job runs |
| `inputs.ENV_NAME` (e.g. `qa-foo`) | Where WG peer secrets are written |

## Step 1 — Create Environment `wg-lifecycle` (UI, ~2 minutes)

In **https://github.com/mosip/infra**:

1. **Settings** → **Environments** → **New environment**
2. Name: `wg-lifecycle` (exact spelling)
3. Enable **Required reviewers** → add yourself + one other person (or a team)
4. Enable **Prevent self-review**
5. Optional: wait timer `1` minute; limit deployment branches to `master`
6. **Save protection rules**

You do **not** need to move secrets yet for the first UI test.

## Step 2 — One-line workflow change

In `.github/workflows/wg-onboard.yml`, under `jobs.onboard`, add:

```yaml
jobs:
  onboard:
    runs-on: [self-hosted, Linux, X64]
    environment: wg-lifecycle          # ← add this line
    timeout-minutes: 20
    steps:
      # ... existing steps unchanged ...
```

Commit on a branch and merge (or test from that branch via **Run workflow** → select the branch).

Full proposed file comment header:

```yaml
# Approval gate: job uses GitHub Environment "wg-lifecycle" (required reviewers).
# That gate is SEPARATE from the target ENV_NAME environment this workflow creates.
```

## Step 3 — Safe test run (DRY_RUN = true)

1. **Actions** → **WireGuard environment onboard/offboard** → **Run workflow**
2. Use:

| Input | Value |
|---|---|
| Branch | branch that contains `environment: wg-lifecycle` |
| `ACTION` | `onboard` |
| `ENV_NAME` | e.g. `wg-approval-test` |
| `JUMPSERVER_HOST` | your usual jumpserver |
| `TICKET` | `TEST-APPROVAL` |
| `DRY_RUN` | **true** (default) |

3. Open the run → job should be **Waiting** on `wg-lifecycle`
4. As **Approver** (not the person who clicked Run): **Review deployments** → Approve
5. Job continues; dry-run logs show planned actions without writing peers/secrets
6. Repeat once with **Reject** to confirm the deny path

## Step 4 — What you should see

| Checkpoint | Expected |
|---|---|
| Before approve | Job status Waiting; no SSH/script steps yet |
| After approve | Steps run; deployment shows actor + approver |
| Self-review | Operator cannot approve own run |
| Reject | Job does not perform onboard |
| DRY_RUN=true | No secret/`assigned.txt` writes |

## Step 5 — Optional hardening (after UX works)

1. Copy `ACTION_PAT` and `MOSIP_AWS_PEM` to **Environment secrets** on `wg-lifecycle`
2. Remove them from repository secrets (so only approved jobs can use them)
3. Only then use `DRY_RUN=false` for a real onboard with a real ticket

## Day-to-day after rollout

| Who | Does |
|---|---|
| QA/Dev operator | Runs workflow with ticket + ENV_NAME |
| DevOps / lead approver | Approves or rejects waiting deployment |
| Same person for both | Blocked if Prevent self-review is on |

## Same pattern for image transfer later

| Action | Gate Environment | Fixed destination |
|---|---|---|
| WG onboard/offboard | `wg-lifecycle` | N/A (target is `ENV_NAME` input) |
| Images → mosipdev2 | `transfer-dev2` | `mosipdev2` |
| Images → mosipqa | `transfer-qa` | `mosipqa` |

WireGuard is the better first test because **dry-run is already the default**.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| No Waiting state | `environment:` missing on that branch | Merge/select correct branch |
| Waiting but no reviewers notified | Required reviewers not saved | Re-open Environment settings |
| Operator can approve self | Prevent self-review off | Enable it |
| Job waits forever | Approver not in list / no access | Add reviewer; grant at least Read on repo |
