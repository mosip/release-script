# Approval-based image transfer — single optional workflow

## Short answer

You **do not need** one YAML per hop. Use **one optional** workflow:

`.github/workflows/image-transfer-with-approval.yml`

**Production today stays:** `.github/workflows/image-transfer.yml` (SECRET_NAME + DESTINATION_ORGANIZATION + existing `MOSIP*_DOCKER_TOKEN` secrets). Merging this PR does **not** break current transfers.

---

## Critical GitHub rule (why the first design was wrong)

A job that calls a reusable workflow with `uses:` **cannot** set `environment:`.

```yaml
# INVALID — actionlint / GitHub reject this
Image-transfer:
  environment: transfer-qa
  uses: mosip/kattu/.github/workflows/image-transfer.yml@master
```

**Valid pattern used here:**

```yaml
approve:
  runs-on: ubuntu-latest
  environment: ${{ inputs.TRANSFER_TARGET }}   # waits for Approver
  steps: ...

Image-transfer:
  needs: [approve, resolve-target]
  uses: mosip/kattu/...                        # no environment on this job
  secrets:
    TOKEN: ${{ secrets[needs.resolve-target.outputs.TOKEN_SECRET] }}
```

Sandbox workflow (`.github/workflows/image-transfer-sandbox.yml`) uses the same valid pattern for fork tests.

---

## What changes when you cut over

| Item | Today (keep working) | After cutover |
|---|---|---|
| Workflow operators run | `image-transfer.yml` | `image-transfer-with-approval.yml` |
| Destination | Free `DESTINATION_ORGANIZATION` | Derived from `TRANSFER_TARGET` |
| Token | Choose `SECRET_NAME` | Mapped to existing `MOSIPDEV2_DOCKER_TOKEN` / `MOSIPQA_DOCKER_TOKEN` / … |
| Approval | None | Environment required reviewers on `TRANSFER_TARGET` |
| Secrets visible? | Never (GitHub write-only) | Same — create/rotate tokens into Environments later for Approach A |

**Approach A (Environment-scoped tokens):** still recommended long-term, but Environment secrets are only readable by jobs that declare that Environment. Because the `uses:` job cannot declare `environment:`, full Environment-secret isolation needs a later change in `mosip/kattu` (gate + token read inside the reusable workflow). Until then, approval still works with **existing repository secrets** after the `approve` job.

---

## GitHub UI (required before using the approval workflow)

Create Environments with names matching `TRANSFER_TARGET`:

| Environment | Required reviewers | Prevent self-review | Pushes to (derived) | Repo secret used today |
|---|---|---|---|---|
| `transfer-dev2` | Dev approvers | Yes | `mosipdev2` | `MOSIPDEV2_DOCKER_TOKEN` |
| `transfer-qa` | QA approvers | Yes | `mosipqa` | `MOSIPQA_DOCKER_TOKEN` |
| `transfer-mosipint` | Release | Yes | `mosipint` | `MOSIPINT_DOCKER_TOKEN` |
| `transfer-mosipid` | Release admins | Yes | `mosipid` | `MOSIPID_DOCKER_TOKEN` |
| `transfer-injistack-*` | Inji / Release | Yes | matching Inji org | `INJISTACK_DOCKER_TOKEN` |

You do **not** need to read old secret values (GitHub never shows them). Keep using the existing repo secrets for the first approval cutover; rotate into Environment secrets later when kattu supports it.

---

## Operator flow (approval workflow)

1. Ticket + PR on `images.txt` (unchanged)  
2. Merge PR  
3. Run **Manual workflow to transfer images (with approval)**  
4. Pick `TRANSFER_TARGET` (+ username / registry)  
5. Job `approve` waits → Approver **Review deployments** → Approve  
6. Transfer runs with the mapped existing Docker token  

---

## What is / is not required in this PR

| Change | Required to keep prod working? | Purpose |
|---|---|---|
| Keep `image-transfer.yml` as today | **Yes** | No breakage |
| Docs (KT, handover, Environments, cutover) | Optional but useful | Training / future cutover |
| `image-transfer-sandbox.yml` | Optional | Test Approve UI on a fork |
| `image-transfer-with-approval.yml` | Optional until cutover | Real approval path |
| CODEOWNERS stub | Optional | Enable when teams ready |

---

## Related docs

- [Sandbox test in your own repo / fork](./image-transfer-sandbox-test.md)
- [Cutover checklist](./image-transfer-cutover-checklist.md)
- [Image Transfer KT (as-is process)](./image-transfer-kt.md)
- [Handover plan](./image-transfer-handover-plan.md)
- [GitHub Environments deep dive](./github-environments-image-transfer.md)
- [Vidivi README](../vidivi/README.md)
