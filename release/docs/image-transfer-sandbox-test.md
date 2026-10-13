# Sandbox test — try approval gates in *your* repo first

Yes. Test the Approve / Reject flow in **your own GitHub repo** (or a fork) before changing `mosip/release-script`.

You do **not** need real Docker Hub push tokens or a real image transfer for the first test. Goal of the sandbox: prove Environment **Waiting → Approve / Reject** works.

---

## What you can prove in a personal repo

| Capability | Can test in your repo? |
|---|---|
| Job waits on Environment | Yes |
| Required reviewers + Prevent self-review | Yes |
| Approve / Reject UI | Yes |
| Environment secret unlocked only after Approve | Yes |
| `TRANSFER_TARGET` → derived destination mapping | Yes (echo / fake job) |
| Real Crane push to `mosipdev2` / `mosipqa` | No (needs MOSIP tokens) — do that only in a controlled pilot later |

---

## Option A — Minimal fake workflow (recommended first, 10 minutes)

### 1. Create a test repo

Example: `youruser/image-transfer-approval-sandbox` (public or private).

Add two GitHub users if possible: **you = operator**, **colleague = approver** (or a second account).  
Approver needs at least **Read**; operator needs **Write**.

### 2. Create Environment

Repo → **Settings** → **Environments** → **New environment**

- Name: `transfer-dev2` (exact)
- Required reviewers: your colleague (not only yourself)
- Enable **Prevent self-review**
- Environment secret: `DOCKER_TOKEN` = any dummy value, e.g. `sandbox-not-a-real-token`

### 3. Add this workflow

File: `.github/workflows/image-transfer-sandbox.yml`

```yaml
name: Sandbox approval transfer

on:
  workflow_dispatch:
    inputs:
      TRANSFER_TARGET:
        description: 'GitHub Environment gate'
        required: true
        type: choice
        default: 'transfer-dev2'
        options:
          - transfer-dev2
          - transfer-qa
      USERNAME:
        description: 'Dummy username'
        required: true
        default: 'sandbox-user'
        type: string

jobs:
  resolve-target:
    runs-on: ubuntu-latest
    outputs:
      DESTINATION_ORGANIZATION: ${{ steps.map.outputs.DESTINATION_ORGANIZATION }}
    steps:
      - id: map
        env:
          TARGET: ${{ inputs.TRANSFER_TARGET }}
        run: |
          case "$TARGET" in
            transfer-dev2) DEST="mosipdev2" ;;
            transfer-qa)   DEST="mosipqa" ;;
            *) echo "Unknown target"; exit 1 ;;
          esac
          echo "DESTINATION_ORGANIZATION=$DEST" >> "$GITHUB_OUTPUT"
          echo "Mapped $TARGET → $DEST"

  # This job waits for Environment approval
  gated-transfer:
    needs: resolve-target
    runs-on: ubuntu-latest
    environment: ${{ inputs.TRANSFER_TARGET }}
    steps:
      - name: Prove secret is available only after Approve
        env:
          TOKEN_PRESENT: ${{ secrets.DOCKER_TOKEN != '' }}
          DEST: ${{ needs.resolve-target.outputs.DESTINATION_ORGANIZATION }}
          USER: ${{ inputs.USERNAME }}
        run: |
          echo "Approver allowed this run"
          echo "Destination would be: $DEST"
          echo "Username: $USER"
          echo "DOCKER_TOKEN present after approval: $TOKEN_PRESENT"
          # Do NOT print the secret value
```

### 4. Run the test

1. **Actions** → **Sandbox approval transfer** → **Run workflow**
2. Pick `transfer-dev2` → Run as **operator**
3. Job `gated-transfer` should show **Waiting**
4. As **approver**: open the run → **Review deployments** → **Approve**
5. Job continues; log shows destination mapping + token present = true
6. Run again → Approver **Reject** → job does not complete the gated steps
7. Run again as operator who is also the only reviewer → with Prevent self-review, they **cannot** approve their own run

If this works, the same pattern will work in `mosip/release-script`.

---

## Option B — Fork of `mosip/release-script` (closer to real YAML)

1. Fork https://github.com/mosip/release-script to your user/org  
2. In **your fork** (not upstream):
   - Create Environments + `DOCKER_TOKEN` (dummy or a token you own for a throwaway Docker org)
   - Merge/copy the approval-based `image-transfer.yml` from PR branch `cursor/image-transfer-handover-plan-9728`
3. Replace the real `uses: mosip/kattu/...` call temporarily with a fake job (like Option A) **or** keep kattu but expect real transfer to fail without valid MOSIP tokens — that is OK if you only care about the Waiting/Approve UI
4. Do **not** open PRs that change upstream until sandbox is proven

**Caution:** Running the real kattu reusable workflow from a fork may still try to copy images if credentials somehow resolve. Prefer Option A, or stub the transfer job in the fork during sandbox.

---

## Option C — Private org “practice” repo with a throwaway Docker Hub org

Only if you want an end-to-end push test:

1. Create Docker Hub org e.g. `yourname-sandbox-dev2`
2. Put a real push token as Environment secret `DOCKER_TOKEN` on `transfer-dev2`
3. Point a minimal copy workflow (Crane `copy`) at that org
4. Still use Environment required reviewers

This proves token unlock + push, without touching MOSIP orgs.

---

## Suggested test matrix (sandbox)

| # | Test | Expected |
|---|---|---|
| 1 | Operator runs → Approver Approves | Waiting then success |
| 2 | Operator runs → Approver Rejects | Gated job stops |
| 3 | Operator = only reviewer, self-review prevented | Cannot approve own run |
| 4 | Wrong/missing Environment name | Job fails or auto-creates ungated env — fix by creating env first |
| 5 | Missing `DOCKER_TOKEN` on Environment | After Approve, secret empty / step fails |

---

## After sandbox passes → real repo

Follow [image-transfer-cutover-checklist.md](./image-transfer-cutover-checklist.md):

1. Create the same Environments on `mosip/release-script` with **real** org tokens  
2. Merge the approval workflow PR  
3. Pilot one small real transfer on `transfer-dev2`  
4. Remove old repo-level Docker tokens  

---

## Testing on https://github.com/Ivanmeneges/release-script

Concrete fork steps (Environments + sandbox workflow + runbook):  
**[image-transfer-test-on-ivan-fork.md](./image-transfer-test-on-ivan-fork.md)**

Ready-made workflow file on this branch:  
`.github/workflows/image-transfer-sandbox.yml`

## Bottom line

| Question | Answer |
|---|---|
| Can I test before changing the actual repo? | **Yes** |
| Best first test? | Option A in your personal repo / fork |
| Need MOSIP Docker tokens for Approve UI? | **No** |
| When to touch `mosip/release-script`? | After sandbox Approve/Reject/self-review tests pass |
