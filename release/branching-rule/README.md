# Branch Protection Rules

Automates applying GitHub branch protection rules across personal and organization repositories using a reusable GitHub Actions workflow.

---

## Repository Structure

```
release-script/                                 ← Caller repo (trigger workflow here)
├── .github/
│   └── workflows/
│       └── branch-protection.yaml             ← Trigger this workflow
└── release/
    └── branching-rule/
        ├── branch-protection.txt              ← Repo + branch list (bulk mode)
        └── custom-branch-protection-rule.yaml ← Custom rules (optional)

kattu/                                         ← Reusable workflow repo
└── .github/
    └── workflows/
        └── branch-protection-rule.yaml        ← Central logic (do not trigger directly)
```

---

## How to Add Repos for Bulk Mode

Edit `release/branching-rule/branch-protection.txt`:

```
repositories:
  - repo: mosip/admin-services
    branch: release-1.2.x

  - repo: inji/vc-verifier
    branch: release-1.8.x

  - repo: Prafulrakhade/admin-services
    branch: develop
```

- `repo` — full name in `org/repo-name` or `user/repo-name` format
- `branch` — exact branch name to protect
- Lines starting with `#` are ignored

---

## How to Run the Workflow

Go to `release-script` → **Actions** → **Apply Branch Protection Rules** → **Run workflow**

### Inputs

| Input | Options | Description |
|---|---|---|
| `mode` | `single` / `bulk` | Single repo or all repos in `branch-protection.txt` |
| `target_repo` | e.g. `mosip/admin-services` | Single mode only — leave blank for bulk |
| `branch_pattern` | e.g. `release-1.2.x` | Single mode only — leave blank for bulk |
| `rules` | `default` / `custom` | Which rules to apply |

### Single Mode
```
mode           → single
target_repo    → mosip/admin-services
branch_pattern → release-1.2.x
rules          → default
```

### Bulk Mode
```
mode           → bulk
target_repo    → (leave blank)
branch_pattern → (leave blank)
rules          → default
```

---

## Access Control

Only users with **Admin** or **Maintain** role on the target repository can trigger the workflow. The check runs in 3 levels:

| Check | Condition | Result |
|---|---|---|
| Check 0 | Actor is the repo owner | Authorized |
| Check 1 | Actor is a direct collaborator with `admin` or `maintain` role | Authorized |
| Check 2 | Actor is a member of any team that has `admin` or `maintain` on the repo | Authorized |

**Blocked roles:**

| Role | Can trigger? |
|---|---|
| Admin | ✅ Yes |
| Maintain | ✅ Yes |
| Write | ❌ No |
| Triage | ❌ No |
| Read | ❌ No |
| Outside collaborator (non-admin/maintain) | ❌ No |

If access is denied, the workflow prints the user's actual role:
```
[DENIED] abhishek8shankar has 'write' role on mosip/admin-services
[DENIED] Only 'admin' and 'maintain' roles can create branch protection rules
```

---

## Existing Branch Protection

If branch protection rules **already exist** on the target branch, the workflow **fails** with a clear error:

```
[FAIL] Branch 'develop' on 'mosip/admin-services'
       already has branch protection rules.
       Please remove the existing rules first if you want to reapply.
```

> Remove the existing rules from GitHub Settings → Branches → Edit, then re-run the workflow.

---

## Default Branch Protection Rules

Applied when `rules → default`:

| Rule | Value |
|---|---|
| Required PR approvals | 1 |
| Dismiss stale reviews | false |
| Require CODEOWNER review | false |
| Require status checks | Auto-discovered |
| Require conversation resolution | true |
| Enforce admins (no bypassing) | true |
| Allow force pushes | false |
| Allow branch deletion | false |
| Require linear history | false |
| Push restrictions (users) | gsasikumar, vishwa-vyom, ckm007 *(org repos only)* |

---

## Custom Branch Protection Rules

Edit `release/branching-rule/custom-branch-protection-rule.yaml` and change only what you need:

```yaml
rules:
  required_approving_review_count: 2      # default: 1
  dismiss_stale_reviews: false
  require_code_owner_reviews: false
  require_last_push_approval: false
  require_status_checks: false
  strict_status_checks: false
  status_check_contexts: ""
  required_conversation_resolution: true
  required_linear_history: false
  enforce_admins: true
  allow_force_pushes: false
  allow_deletions: false
  push_users: "gsasikumar,vishwa-vyom,ckm007"
  push_teams: ""
```

Then run workflow with `rules → custom`.

> Inline comments (`# ...`) are supported and ignored by the parser.

---

## Status Checks — Auto Discovery

For `default` mode, the workflow automatically reads workflow files in the **target repo** and registers:

- Jobs using `maven-build.yml` → `<job-id> / maven-build`
- Jobs using `docker-build.yml` → `<SERVICE_NAME> / build-dockers`

If no matching jobs found → branch protection is still applied without status checks.

---

## Personal vs Organization Repos

| Feature | Personal repo | Org repo |
|---|---|---|
| All protection rules | ✅ | ✅ |
| Push restrictions (users/teams) | ❌ Skipped automatically | ✅ |

Push restrictions are silently skipped for personal repos — GitHub API does not support them for personal accounts.

---

## Required Secrets

Configure in `release-script` → **Settings → Secrets → Actions**:

| Secret | Required | Description |
|---|---|---|
| `ACTION_PAT` | ✅ Yes | PAT with `repo` + `admin:org` scopes |
| `ALLOWED_TEAM` | ❌ No | Legacy — no longer required, team check is automatic |

### Creating the PAT
1. GitHub → **Settings → Developer settings → Personal access tokens → Tokens (classic)**
2. Select scopes: `repo` (full) + `admin:org`
3. Save as `ACTION_PAT` secret in `release-script`

---

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `branch-protection.txt not found` | File not at `release/branching-rule/branch-protection.txt` | Check file path and branch |
| `Access denied` | User does not have Admin or Maintain role | Grant correct role on target repo |
| `Already has branch protection rules` | Rules exist on target branch | Remove existing rules first |
| `HTTP 422 Validation Failed` | Push restrictions on personal repo | Expected — handled automatically |
| `HTTP 404 on branch` | Branch does not exist | Create the branch first |
| `Custom rules file not found` | File missing | Ensure file exists at `release/branching-rule/custom-branch-protection-rule.yaml` |
