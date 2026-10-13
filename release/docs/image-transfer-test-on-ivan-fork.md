# Test approval on https://github.com/Ivanmeneges/release-script

This is the concrete checklist for **your fork**. Agent cannot push to that repo; you apply these steps locally (or via GitHub UI).

---

## Goal

Prove **Waiting → Approve / Reject** on your fork before changing `mosip/release-script`.  
Use the **sandbox** workflow (no real Docker push, no MOSIP tokens).

---

## Step 1 — Put the sandbox workflow on your fork

### Option A — GitHub UI (fastest)

1. Open https://github.com/Ivanmeneges/release-script  
2. Create file: `.github/workflows/image-transfer-sandbox.yml`  
3. Paste contents from this PR branch file:  
   https://github.com/mosip/release-script/blob/cursor/image-transfer-handover-plan-9728/.github/workflows/image-transfer-sandbox.yml  
4. Commit to branch `release-1.2.0.1` (or a new branch `approval-sandbox`)

### Option B — Local git

```bash
git clone https://github.com/Ivanmeneges/release-script.git
cd release-script
git checkout -b approval-sandbox

# Copy sandbox workflow from the MOSIP PR branch
curl -fsSL \
  https://raw.githubusercontent.com/mosip/release-script/cursor/image-transfer-handover-plan-9728/.github/workflows/image-transfer-sandbox.yml \
  -o .github/workflows/image-transfer-sandbox.yml

git add .github/workflows/image-transfer-sandbox.yml
git commit -m "test: add sandbox approval-gate workflow"
git push -u origin approval-sandbox
```

---

## Step 2 — Create Environments on your fork

On **https://github.com/Ivanmeneges/release-script** (not mosip):

**Settings** → **Environments** → **New environment**

### Create `transfer-dev2`

1. Name: `transfer-dev2`  
2. **Required reviewers**: add a second person (colleague). If alone, add yourself for now and test Reject first; for self-review test you need a second account.  
3. Enable **Prevent self-review** (needs a second reviewer to fully prove)  
4. **Add environment secret**:
   - Name: `DOCKER_TOKEN`
   - Value: `sandbox-dummy-token` (any string)  
5. Save

### Optional: create `transfer-qa` the same way

Same secret name `DOCKER_TOKEN`, different dummy value if you like.

---

## Step 3 — Enable Actions on the fork (if needed)

Forks sometimes have Actions disabled:

**Settings** → **Actions** → **General** → allow Actions → Save

---

## Step 4 — Run the sandbox

1. https://github.com/Ivanmeneges/release-script/actions  
2. Workflow: **Sandbox — approval gate for image transfer**  
3. **Run workflow**
   - Branch: the one with the sandbox YAML  
   - `TRANSFER_TARGET`: `transfer-dev2`  
   - `USERNAME`: anything  
4. Open the run → job `gated-transfer` should be **Waiting**  
5. **Review deployments** → Approve  
6. Job should succeed and log: derived destination `mosipdev2`, `DOCKER_TOKEN present=true`

### Also test

| Test | How | Expected |
|---|---|---|
| Reject | Run again → Reject | Gated job does not succeed |
| Self-review blocked | You start run; you try to approve | Blocked if Prevent self-review + you are the actor |
| Missing secret | Remove `DOCKER_TOKEN`, Approve | Fails after approval with clear error |

---

## Step 5 — (Optional) Try the real approval `image-transfer.yml` on the fork

Only after sandbox works:

```bash
# On your fork clone
curl -fsSL \
  https://raw.githubusercontent.com/mosip/release-script/cursor/image-transfer-handover-plan-9728/.github/workflows/image-transfer.yml \
  -o .github/workflows/image-transfer.yml
git add .github/workflows/image-transfer.yml
git commit -m "test: approval-based image-transfer.yml on fork"
git push
```

**Note:** The real workflow calls `mosip/kattu` and needs a real `DOCKER_TOKEN` that can push. On the fork, either:

- Keep using **sandbox** only, or  
- Temporarily replace the `uses: mosip/kattu/...` job with the sandbox `gated-transfer` steps so you still don’t push real images

Do **not** put real MOSIP org tokens on a personal fork long-term.

---

## Step 6 — After fork tests pass

1. On `mosip/release-script`, follow [cutover checklist](./image-transfer-cutover-checklist.md)  
2. Create real Environments + real `DOCKER_TOKEN` values there  
3. Merge PR https://github.com/mosip/release-script/pull/1786  
4. Pilot one small real transfer  

---

## Links

| Item | URL |
|---|---|
| Your fork | https://github.com/Ivanmeneges/release-script |
| Sandbox workflow (PR branch) | https://github.com/mosip/release-script/blob/cursor/image-transfer-handover-plan-9728/.github/workflows/image-transfer-sandbox.yml |
| Generic sandbox guide | [image-transfer-sandbox-test.md](./image-transfer-sandbox-test.md) |
| MOSIP PR | https://github.com/mosip/release-script/pull/1786 |
