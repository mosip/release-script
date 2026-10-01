# Knowledge Transfer: Current Image Transfer Process

**Audience:** DevOps, Dev, QA, Release engineers who need to understand or execute Docker image transfers today  
**Repo:** [`mosip/release-script`](https://github.com/mosip/release-script)  
**Tooling:** Vidivi (`release/vidivi/`) + GitHub Actions workflow `image-transfer.yml`  
**Status:** This document describes the **present** (as-is) process. Future handover / Environment approval controls are separate docs.

---

## 1. What problem does image transfer solve?

CI builds push images into a **development** Docker Hub org (for example `mosipdev` or `injistackdev`). Other stages (pre-QA, QA, interim, production) use **different orgs**. We do **not** rebuild the image for each stage; we **copy** the same image (via Crane) from source org/tag to destination org/tag.

That copy is what we call **image transfer**.

```
Build (CI) ──push──► mosipdev ──transfer──► mosipdev2 ──transfer──► mosipqa ──transfer──► mosipid
                                              │                       │
                                              │                       └──► mosipint (optional / patches)
                                         pre-QA staging              QA testing
```

---

## 2. Docker Hub organizations (MOSIP + Inji)

### MOSIP path

| Org | Purpose | Typical who asks for transfer |
|---|---|---|
| `mosipdev` | CI-built / early Dev images | — (created by build pipelines) |
| `mosipdev2` | Pre-QA staging / stabilization | Dev / module owners |
| `mosipqa` | Images for QA test environments | Dev / QA after Dev2 validation |
| `mosipint` | Interim / implementation / patch holding | Release / DevOps |
| `mosipid` | Community / production release images | Release / DevOps (+ Security signing after) |

### Inji parallel path (same idea, different org names)

| Org | Role |
|---|---|
| `injistackdev` | Dev |
| `injistackdev2` | Pre-QA |
| `injistackqa` | QA |
| `injistack` | Released / production-equivalent |

Lifecycle (recommended):

```
mosipdev → mosipdev2 → mosipqa → mosipid
```

Staged / patch path:

```
mosipdev → mosipdev2 → mosipqa → mosipint → mosipid
```

---

## 3. Components you will touch

| Piece | Path / link | Role |
|---|---|---|
| Image list | `release/vidivi/images.txt` | **Only** file changed in a normal transfer PR |
| Transfer tool | `release/vidivi/vidivi.py` | Local `check` / `hash` / `push` (optional; Actions uses this via reusable workflow) |
| Manual workflow | [Actions → Manual workflow to transfer images](https://github.com/mosip/release-script/actions/workflows/image-transfer.yml) | How transfers are executed in practice |
| Reusable logic | `mosip/kattu` → `image-transfer.yml` | Actual Crane copy + protections (e.g. `mosipid` admin-only) |
| Report | `release/vidivi/transfer_report.md` | Summary after an Actions run |
| Tool docs | [`release/vidivi/README.md`](../vidivi/README.md) | Inputs, secrets, troubleshooting |
| Release context | [`release/README.md`](../README.md) | Where transfer sits in a full release |

---

## 4. End-to-end process (as followed today)

### High-level flow

```
1. Need identified (sprint / bugfix / release)
2. DSD/Jira ticket created
3. Update release/vidivi/images.txt (source:tag → dest-tag)
4. Open PR on release-script (usually release-1.2.0.1 or active release branch)
5. PR reviewed & merged
6. Run GitHub Actions "Manual workflow to transfer images"
7. Select destination secret + destination org
8. Workflow: validate token → check images → Crane copy → Slack / report
9. Verify images on destination org
10. Close ticket (for prod: also Security signing ticket)
```

### Step-by-step (operator checklist)

#### Step 1 — Confirm what must move

Collect:

- Source org + image name + **source tag** (must already exist)
- Destination org
- Destination tag (often same version line, sometimes shortened, e.g. `release-1.0.x` → `1.0.x`)
- Ticket id (e.g. `DSD-10681`)

Confirm source image exists, for example:

```bash
crane digest mosipdev/partner-management-service:release-1.2.2.x
# or
docker pull mosipdev/partner-management-service:release-1.2.2.x
```

#### Step 2 — Create / use the DSD ticket

Title pattern used in practice:

- `[DSD-xxxxx] Image transfer from dev to dev2`
- `[DSD-xxxxx] Image transfer from mosipdev to mosipqa`
- `[DSD-xxxxx] injistackdev2 to injistackqa`

Ticket should list images/tags and reason (module release, QA handoff, patch, etc.).

#### Step 3 — Edit `images.txt`

File: `release/vidivi/images.txt`

**Format (space-separated, one image per line):**

```
<source-org>/<image>:<source-tag> <destination-tag>
```

Examples:

```
mosipdev/apitest-resident:develop develop
injistackdev2/uitest-web:release-1.0.x 1.0.x
mosipqa/kernel-auth-service:1.2.0.1 1.2.0.1
```

Notes:

- Destination **org is not** in this file — you choose it when running the workflow (`DESTINATION_ORGANIZATION`).
- The file is usually **replaced** for the next transfer batch (not an ever-growing append-only list). Recent PRs overwrite previous lines with the new set.
- Official library images (postgres, nginx) can be listed without `library/`.

#### Step 4 — Open PR on `release-script`

- Base branch: active release branch (commonly `release-1.2.0.1`)
- Title: match ticket, e.g. `[DSD-10761] Image transfer from dev to dev2 .`
- Change set: almost always **only** `release/vidivi/images.txt`
- Get PR reviewed and **merged** before running the workflow (workflow reads the file from the branch you select)

#### Step 5 — Run the manual workflow

1. Open [Manual workflow to transfer images](https://github.com/mosip/release-script/actions/workflows/image-transfer.yml)
2. Click **Run workflow**
3. Select the **branch** that contains the merged `images.txt`
4. Fill inputs (see cheat sheet below)
5. Run and watch the job

#### Step 6 — Verify

- Actions run succeeded
- Spot-check on Docker Hub / Harbor that destination tags exist
- Optional: `crane digest <dest-org>/<image>:<tag>` matches source
- Attach run URL on the ticket; close ticket
- For **`mosipid`**: open Security image-signing ticket (release process)

---

## 5. Workflow inputs cheat sheet (present process)

| Input | Meaning |
|---|---|
| `USERNAME` | Docker Hub user or Harbor robot that can **push** to destination |
| `SECRET_NAME` | Which GitHub secret holds the destination token |
| `CUSTOM_SECRET_NAME` | Only if `SECRET_NAME=custom` |
| `DESTINATION_ORGANIZATION` | Dest org/project (`mosipdev2`, `mosipqa`, `mosipid`, …) |
| `REGISTRY_URL` | Default Docker Hub: `https://index.docker.io/v1/` |
| `REGISTRY_TYPE` | `dockerhub` / `harbor` / `other` |
| `ENABLE_WIREGUARD` | `true` for private Harbor behind VPN |

### Typical combinations

| Hop | `SECRET_NAME` | `DESTINATION_ORGANIZATION` |
|---|---|---|
| → `mosipdev2` | `MOSIPDEV2_DOCKER_TOKEN` | `mosipdev2` |
| → `mosipqa` | `MOSIPQA_DOCKER_TOKEN` | `mosipqa` |
| → `mosipint` | `MOSIPINT_DOCKER_TOKEN` | `mosipint` |
| → `mosipid` | `MOSIPID_DOCKER_TOKEN` | `mosipid` |
| → Inji orgs | `INJISTACK_DOCKER_TOKEN` or `custom` | e.g. `injistackqa` / `injistackdev2` |

**Protected destination:** transfers to `mosipid` require **admin** on the calling repo (enforced in `mosip/kattu`). Non-admins should not use this for production.

---

## 6. Scenario-based examples (from merged PRs)

These are real merged PRs on `mosip/release-script`. Use them in KT to show “what good looks like.”

### Scenario A — Dev → Dev2 (pre-QA staging)

**When:** New builds are ready for pre-QA / stabilization in `mosipdev2` (or Inji `injistackdev2`).

**Example PR:** [#1812](https://github.com/mosip/release-script/pull/1812) — `[DSD-10761] Image transfer from dev to dev2`  
**Author:** abhishek8shankar · **Merged:** 2026-09-01 · **Base:** `release-1.2.0.1`

`images.txt` content after PR:

```
mosipdev/apitest-resident:develop develop
```

**Meaning:**

- Pull/copy from `mosipdev/apitest-resident:develop`
- Push as `mosipdev2/apitest-resident:develop` (dest org chosen in workflow)

**Another Dev→Dev2 example:** [#1797](https://github.com/mosip/release-script/pull/1797) — `[DSD-10681]`

```
injistackdev/uitest-web:release-1.0.x release-1.0.x
injistackdev/apitest-mimoto:release-1.0.x release-1.0.x
```

**Workflow run (conceptual):**

| Field | Value |
|---|---|
| Branch | `release-1.2.0.1` |
| `SECRET_NAME` | `MOSIPDEV2_DOCKER_TOKEN` (or Inji token if dest is injistackdev2) |
| `DESTINATION_ORGANIZATION` | `mosipdev2` or `injistackdev2` |

**KT talking points:**

- Ticket id in PR title
- Only `images.txt` changed
- Source org in file = where image already lives
- Destination org = workflow input, not the file

---

### Scenario B — Same ticket, second hop Dev2 → QA

**When:** Images validated on Dev2; QA needs them in `mosipqa` / `injistackqa`.

**Paired PRs under the same ticket `DSD-10681`:**

1. [#1797](https://github.com/mosip/release-script/pull/1797) — Dev → Dev2 (sources from `injistackdev`)
2. [#1798](https://github.com/mosip/release-script/pull/1798) — Dev2 → QA (sources from `injistackdev2`)

`images.txt` in #1798:

```
injistackdev2/uitest-web:release-1.0.x 1.0.x
injistackdev2/apitest-mimoto:release-1.0.x 1.0.x
```

**Notice:**

- Source org changed from `injistackdev` → `injistackdev2` (because images now live on Dev2)
- Destination tag shortened to `1.0.x` while source tag stayed `release-1.0.x`
- Separate PR + separate workflow run for the second hop (do not mix hops in one unclear batch)

**Workflow:** `DESTINATION_ORGANIZATION=injistackqa` (or `mosipqa`), matching QA token.

**Similar MOSIP pairs:**

| Ticket | Dev → Dev2 | Dev2 → QA |
|---|---|---|
| DSD-10600 | [#1770](https://github.com/mosip/release-script/pull/1770) | [#1772](https://github.com/mosip/release-script/pull/1772) |
| DSD-10588 | [#1763](https://github.com/mosip/release-script/pull/1763) | [#1764](https://github.com/mosip/release-script/pull/1764) |

**KT talking points:**

- One hop per PR/run is the clean pattern
- After Dev→Dev2 succeeds, next PR sources from **dev2**, not still from **dev**
- Same DSD ticket can cover both hops, but each hop is its own PR

---

### Scenario C — Direct-ish Dev → QA

**When:** Team requests images straight into QA org (still via transfer; sources listed from `mosipdev`).

**Example PR:** [#1789](https://github.com/mosip/release-script/pull/1789) — `[DSD-10643] image transfer from mosipdev to mosipqa`  
**Author:** Ivanmeneges · **Merged:** 2026-08-07

```
mosipdev/partner-management-service:release-1.2.2.x 1.2.2.x
mosipdev/policy-management-service:release-1.2.2.x 1.2.2.x
```

**Workflow:** `SECRET_NAME=MOSIPQA_DOCKER_TOKEN`, `DESTINATION_ORGANIZATION=mosipqa`

**KT talking points:**

- File still lists **source** as `mosipdev/...`
- Recommended lifecycle prefers Dev2 first; direct Dev→QA happens when teams request it / for specific modules — call out risk (less pre-QA soak)
- Similar: [#1766](https://github.com/mosip/release-script/pull/1766), [#1750](https://github.com/mosip/release-script/pull/1750)

---

### Scenario D — QA → Interim (`mosipint` / Inji QA → int-style)

**When:** QA-validated images needed for interim / implementation holding.

**Example PR:** [#1768](https://github.com/mosip/release-script/pull/1768) — `[DSD-10599] Image transfer from qa to int`  
**Author:** abhishek8shankar · **Merged:** 2026-07-30

```
injistackqa/mimoto:1.0.x 1.0.x
injistackqa/inji-web:1.0.x 1.0.x
```

**Workflow:** destination org `mosipint` or the intended interim/Inji dest; use `MOSIPINT_DOCKER_TOKEN` when pushing to `mosipint`.

**KT talking points:**

- Source is now the **QA** org
- Interim is Release/DevOps-sensitive; treat carefully vs routine Dev2 hops

---

### Scenario E — Toward production / community (`mosipid`) + infra images

**When:** Release or shared infra images must land on `mosipid` / `mosipint`.

**Example PR:** [#1813](https://github.com/mosip/release-script/pull/1813) — `[DSD-10771] moved the docker kafka and zookeeper docker image to mosipid and mosipint`  
**Author:** Prafulrakhade · **Merged:** 2026-09-02

```
praful02/kafka:3.5.1-debian-11-r0 3.5.1-debian-11-r0
praful02/zookeeper:3.8.2-debian-11-r4 3.8.2-debian-11-r4
```

**KT talking points:**

- Source can be a non-`mosipdev` org when promoting third-party/mirrored images
- May require **two** workflow runs if pushing to both `mosipid` and `mosipint` (same `images.txt`, different `DESTINATION_ORGANIZATION` / secrets)
- `mosipid` is **admin-protected** in `kattu`
- After community/prod transfer: create **Security image signing** ticket (see `release/README.md` step 13)

---

### Scenario F — Inji Dev2 → Inji QA (explicit org rename in file)

**Example PR:** [#1809](https://github.com/mosip/release-script/pull/1809) — `[DSD-10756] injistackdev2 to injistackqa`

Diff pattern: sources switched to `injistackdev2/...` before transfer into QA.

Related nearby:

- [#1808](https://github.com/mosip/release-script/pull/1808) — injistackdev → injistackdev2  
- [#1806](https://github.com/mosip/release-script/pull/1806) / [#1807](https://github.com/mosip/release-script/pull/1807) — mosipdev → mosipdev2 → mosipqa chain

**KT talking points:** Inji follows the same PR + workflow ritual; only org names and sometimes tokens differ.

---

## 7. How to walk a KT session (suggested agenda)

| Time box | Topic | Demo artifact |
|---|---|---|
| 5 min | Why transfer exists / org map | Section 2 diagram |
| 10 min | File format + PR ritual | Open [#1812](https://github.com/mosip/release-script/pull/1812) diff |
| 10 min | Two-hop story | [#1797](https://github.com/mosip/release-script/pull/1797) → [#1798](https://github.com/mosip/release-script/pull/1798) |
| 10 min | Workflow UI + secret/org pairing | Live Actions form (dry explanation if no run) |
| 5 min | Prod / signing / admin protection | [#1813](https://github.com/mosip/release-script/pull/1813) + `release/README.md` |
| 5 min | Failures & checklist | Section 9 |
| 5 min | Q&A / who does what today | Section 8 |

---

## 8. Who does what today (as-is)

| Activity | Typical owner today |
|---|---|
| Build images into `mosipdev` / `injistackdev` | Module CI / developers |
| Raise DSD ticket + PR updating `images.txt` | Requester (Dev / QA / DevOps) — many PRs from DevOps engineers |
| Merge transfer PR | Reviewers with write access on release branch |
| Run Actions transfer workflow | Usually DevOps (holds org tokens / knows secret mapping) |
| Verify destination tags | Requester + DevOps |
| Transfer to `mosipid` / signing ticket | Release / DevOps + Security |

> Note: Handover of Dev→Dev2 / Dev2→QA to Dev/QA teams is a **future** control change (Environments, stage workflows). This KT is the **current** operating procedure.

---

## 9. Common mistakes & troubleshooting

| Mistake / symptom | Why it hurts | What to do |
|---|---|---|
| Wrong source org in `images.txt` | Workflow looks for image that is not there | After Dev2 hop, source must be `*dev2`, not still `*dev` |
| Dest org in file instead of workflow | File format has no dest org | Put dest only in `DESTINATION_ORGANIZATION` |
| Ran workflow before PR merge | Branch still has old list | Merge first; select correct branch |
| Secret / org mismatch | Auth fail or push to wrong place | Match cheat sheet (Section 5) |
| Tag does not exist on source | `check` fails | Confirm digest/pull before PR |
| Overwrote `images.txt` for unrelated batch still needed | Previous list lost from tip of branch | OK for process (file is per-run manifest); keep ticket/PR history as audit |
| Non-admin → `mosipid` | Blocked by `kattu` | Use Release admin or request admin-run |
| Harbor timeout | Private network | `ENABLE_WIREGUARD=true` + valid `WIREGUARD_CONFIG` |
| CRLF / spacing in `images.txt` | Parse issues | One space between image and dest tag; Unix line endings |

**Local dry checks (optional):**

```bash
cd release/vidivi
# configure config.yml for the destination you intend
python3 vidivi.py check
python3 vidivi.py hash   # optional digest compare
# prefer Actions push in shared process; local push only if you have tokens & policy allows
```

---

## 10. Quick reference card (print / slide)

1. Ticket (`DSD-…`)  
2. Edit `release/vidivi/images.txt` → `source-org/image:src-tag dest-tag`  
3. PR → merge on release branch  
4. Actions → Manual image transfer → branch + secret + **destination org**  
5. Verify tags / digests → close ticket  
6. If `mosipid`: Security signing ticket  

**Remember:** `images.txt` = **what** to copy from where; workflow inputs = **where** to push and **which credential**.

---

## 11. Reference PR index (recent patterns)

| PR | Hop (from title) | Useful for |
|---|---|---|
| [#1812](https://github.com/mosip/release-script/pull/1812) | Dev → Dev2 | Single-image Dev2 handoff |
| [#1797](https://github.com/mosip/release-script/pull/1797) / [#1798](https://github.com/mosip/release-script/pull/1798) | Dev→Dev2 then Dev2→QA | Same ticket, two hops |
| [#1789](https://github.com/mosip/release-script/pull/1789) | Dev → QA | Direct-to-QA request |
| [#1768](https://github.com/mosip/release-script/pull/1768) | QA → Int | Interim promotion |
| [#1813](https://github.com/mosip/release-script/pull/1813) | → mosipid / mosipint | Prod-bound / infra images |
| [#1809](https://github.com/mosip/release-script/pull/1809) | injistackdev2 → injistackqa | Inji QA path |
| [#1806](https://github.com/mosip/release-script/pull/1806) / [#1807](https://github.com/mosip/release-script/pull/1807) | mosipdev → dev2 → qa | Full lower-stage chain |

Search more: GitHub PRs filter `is:merged image transfer` in `mosip/release-script`.

---

## 12. Related docs

| Doc | Use |
|---|---|
| [Vidivi README](../vidivi/README.md) | Tool details, secrets, Harbor, Crane |
| [Release README](../README.md) | Where transfer sits in full release |
| [Image transfer handover plan](./image-transfer-handover-plan.md) | Future Dev/QA ownership model |
| [GitHub Environments how-to](./github-environments-image-transfer.md) | Future approval gates |
| [WG approval test](./wg-lifecycle-approval-test.md) | Practising Environment Approve/Reject |

---

**Document purpose:** Enable anyone to explain and execute the **current** MOSIP/Inji image transfer process using real release-script PRs as teaching examples.
