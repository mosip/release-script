# Vidivi - Docker Image Transfer Tool

`vidivi.py` is a Python script used to transfer Docker images between container registries as part of the MOSIP release process. It supports transferring images between different Docker Hub organizations or to private registries like Harbor.

## Overview

For a step-by-step **Knowledge Transfer** on the current process (with scenario examples from merged PRs), see **[Image Transfer KT](../docs/image-transfer-kt.md)**.

For handing stage transfers (`mosipdev` → `mosipdev2`, `mosipdev2` → `mosipqa`) from DevOps to Dev/QA with access control, approvals, and monitoring, see **[Image Transfer Handover Plan](../docs/image-transfer-handover-plan.md)** and **[GitHub Environments setup (full steps)](../docs/github-environments-image-transfer.md)**.

In MOSIP, we maintain several Docker Hub organizations with specific purposes:

* **`mosipid`**: Contains officially released Docker images for the Open Source Community
* **`mosipint`**: 
    * Contains images not yet officially released but eligible for specific implementations
    * Holds patches for services until fully released
    * Maintains backups of QA-tested images from previous internal sprints
    * Images from here eventually move to `mosipid`
* **`mosipdev`**: Contains Docker images in the development phase
* **`mosipdev2`**: Intermediate staging environment for images before QA testing
* **`mosipqa`**: Holds Docker images provided to the QA team for testing

## Docker Image Lifecycle

MOSIP follows two primary release flows depending on the release strategy:

### Flow 1: Direct Release Path (Recommended)
```
mosipdev → mosipdev2 → mosipqa → mosipid
```

* **mosipdev**: Newly created images from CI/CD, undergoing initial dev testing
* **mosipdev2**: Intermediate staging for pre-QA validation and stabilization
* **mosipqa**: Images verified in mosipdev2, sent to QA team for comprehensive testing
* **mosipid**: Images that passed all QA testing, ready for production release

**Use Case**: Standard releases where images are stable and ready for production after QA validation.

### Flow 2: Staged Release Path (With Interim Release)
```
mosipdev → mosipdev2 → mosipqa/mosipint → mosipid
```

* **mosipdev**: Newly created images from CI/CD, undergoing initial dev testing
* **mosipdev2**: Intermediate staging for pre-QA validation and stabilization
* **mosipqa**: Images verified in mosipdev2, sent to QA team for comprehensive testing
* **mosipint**: QA-verified images staged for specific implementations or interim releases
  * Used for patches that need immediate deployment
  * Holds stable images from previous sprints as backup
  * Acts as a holding area before final production release
* **mosipid**: Final production release after successful deployment validation in mosipint

**Use Case**: 
- Critical patches requiring staged rollout
- Images needing validation in specific implementation environments before full release
- Maintaining stable interim versions while next version is in QA

### Choosing the Right Flow

| Scenario | Recommended Flow | Reason |
|----------|------------------|--------|
| Regular sprint release | Flow 1 (Direct) | Faster time to production |
| Critical security patch | Flow 2 (Staged) | Allows validation before wide release |
| Breaking changes | Flow 2 (Staged) | Test in limited implementations first |
| Minor bug fixes | Flow 1 (Direct) | Low risk, direct path sufficient |
| Major version upgrade | Flow 2 (Staged) | Additional validation layer needed |

## Key Features

✅ **Universal Image Transfer**: Works with any OCI-compliant container registry (Docker Hub, Harbor, ACR, ECR, GCR, etc.)  
✅ **Multi-Architecture Support**: Automatically preserves all architectures (amd64, arm64, arm/v7, etc.) using Crane  
✅ **Parallel Processing**: Configurable concurrent image transfers for faster operations  
✅ **VPN Support**: Optional WireGuard VPN for private registry access  
✅ **Three Operation Modes**: `check`, `hash`, and `push` for validation and transfer  

## Architecture

The tool uses **Crane** (from Google's go-containerregistry project) for all image transfers, which:
- Automatically handles both single-architecture and multi-architecture images
- Preserves complete manifest lists with all platform variants
- Works with any OCI-compliant registry (Docker Hub, Harbor, ACR, ECR, etc.)
- Supports HTTP and HTTPS registries

## Prerequisites

### Required Tools
- **Python 3.9+**
- **Docker** (for registry authentication)
- **Crane** - Install with:
  ```bash
  # Linux
  curl -sL https://github.com/google/go-containerregistry/releases/latest/download/go-containerregistry_Linux_x86_64.tar.gz | sudo tar -xzC /usr/local/bin crane
  
  # macOS
  brew install crane
  
  # Verify installation
  crane version
  ```

### Python Dependencies
```bash
pip install docker requests urllib3 PyYAML
```

## Configuration

### 1. Update `config.yml`

```yaml
docker:
  username: "your-username"                          # Registry username
  token: "your-token-or-password"                    # Registry token/password
  registry_url: "https://index.docker.io/v1/"        # Destination registry URL
  destination_organization: "mosipid"                # Destination org/project
  imageExitUrl: "https://registry-1.docker.io/v2/"   # Source registry API URL

csv:
  filename: "images.txt"                             # Image list file
  has_header: false

process:
  count: 3                                           # Parallel workers (1-10)
```

**Registry URL Examples**:
- Docker Hub: `https://index.docker.io/v1/`
- Harbor: `https://harbor.example.com` or `http://harbor.example.com` (for HTTP)
- ACR: `https://myregistry.azurecr.io`
- ECR: `https://123456789.dkr.ecr.us-east-1.amazonaws.com`
- GCR: `https://gcr.io`

**Harbor Robot Account Format**:
- Username: `robot$projectname+robotname` (e.g., `robot$mosipdev+release-bot`)
- Token: Robot account token from Harbor UI

### 2. Update `images.txt`

List images to transfer with space-separated source and destination tags:

```
mosipdev/kernel-auth-service:1.2.0.1 1.2.0.1
mosipdev/kernel-masterdata-service:1.2.0.1 1.2.0.1
mosipdev/pre-registration-application-service:1.2.0.1 1.2.0.1
postgres:13 13
nginx:latest latest
```

**Format**: `source-image:source-tag destination-tag`

**Official Docker Hub Images**: For library images like `postgres`, `nginx`, `redis`, just use the image name directly (no `library/` prefix needed).

## Usage

### Local Execution

```bash
cd release/vidivi

# 1. Check if source images exist
python3 vidivi.py check

# 2. Compare source and destination image hashes (optional)
python3 vidivi.py hash

# 3. Transfer images
python3 vidivi.py push
```

### Operation Modes

| Mode | Description | Exit on Error |
|------|-------------|---------------|
| `check` | Validates source images exist on Docker Hub | Yes (if images missing) |
| `hash` | Compares image digests between source and destination | No (informational) |
| `push` | Performs actual image transfer using Crane | Yes (on transfer failure) |

### Output

```
🚀 Starting image transfer with crane (unified approach)...
********** [ mosipid/kernel-auth-service:1.2.0.1 ] ********************
Transferring image using crane...
Executing: crane copy mosipdev/kernel-auth-service:1.2.0.1 registry.example.com/mosipid/kernel-auth-service:1.2.0.1
✅ Successfully transferred image with crane
✅ Image available at: registry.example.com/mosipid/kernel-auth-service:1.2.0.1
✅ Crane automatically preserves all architectures and manifest structures
```

## GitHub Actions Workflow

### Workflow Inputs

Execute the [Manual workflow to transfer images](https://github.com/mosip/release-script/actions/workflows/image-transfer.yml) from the **release-script** repository.

| Input | Description | Required | Default | Example |
|-------|-------------|----------|---------|---------|
| `USERNAME` | Registry username | Yes | - | `robot$mosipdev+release-bot` (Harbor)<br>`myusername` (Docker Hub) |
| `SECRET_NAME` | Select the GitHub secret name for Docker registry token (dropdown) | Yes | `MOSIPDEV2_DOCKER_TOKEN` | `MOSIPID_DOCKER_TOKEN`, `custom` |
| `CUSTOM_SECRET_NAME` | Custom secret name (only required if `SECRET_NAME` is set to `custom`) | No | - | `MY_ORG_DOCKER_TOKEN` |
| `DESTINATION_ORGANIZATION` | Destination org/project | Yes | - | `mosipid`, `mosipqa`, `myproject` |
| `REGISTRY_URL` | Destination registry URL | Yes | `https://index.docker.io/v1/` | `https://harbor.example.com` |
| `REGISTRY_TYPE` | Registry type | Yes | `dockerhub` | `dockerhub`, `harbor`, `other` |
| `ENABLE_WIREGUARD` | Enable VPN for private networks | No | `false` | `true` or `false` |

**`SECRET_NAME` Options:**

| Option | Description |
|---|---|
| `MOSIPDEV2_DOCKER_TOKEN` | Token for `mosipdev2` organization |
| `MOSIPQA_DOCKER_TOKEN` | Token for `mosipqa` organization |
| `MOSIPID_DOCKER_TOKEN` | Token for `mosipid` organization |
| `MOSIPINT_DOCKER_TOKEN` | Token for `mosipint` organization |
| `INJISTACK_DOCKER_TOKEN` | Token for `injistack` organization |
| `custom` | Enter your own secret name in `CUSTOM_SECRET_NAME` field |

### Workflow Secrets

**Required Secrets:**
1. **`<SECRET_NAME>`**: Registry authentication token — select from predefined options or provide a custom name
   - Docker Hub: Personal Access Token or Account Password
   - Harbor: Robot account token
   - Other registries: Appropriate authentication token

2. **`SLACK_WEBHOOK_DEVOPS`**: Slack notification webhook (shared across all workflows)

3. **`WIREGUARD_CONFIG`**: (Optional) WireGuard VPN configuration for private registries

**Custom SECRET_NAME Validation:**

When `SECRET_NAME` is set to `custom`, the `CUSTOM_SECRET_NAME` field is **required** and validated:
- Must start with a letter or underscore
- Can only contain letters, numbers, and underscores (`[A-Za-z0-9_]`)
- No spaces, hyphens, or special characters

| `CUSTOM_SECRET_NAME` | Valid? |
|---|---|
| `MY_ORG_DOCKER_TOKEN` | ✅ |
| `_PRIVATE_TOKEN` | ✅ |
| `my-org-token` | ❌ Hyphens not allowed |
| `MY SECRET` | ❌ Spaces not allowed |
| *(empty)* | ❌ Required when `custom` is selected |

**How to Add Secrets:**
1. Go to GitHub repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Create the secret with the exact name you will provide as `SECRET_NAME` input
4. Set the value to your Docker registry token/password

**Protected Organizations:**

Certain destination organizations (e.g., `mosipid`) are protected in the `mosip/kattu` reusable workflow. Transfers to protected organizations require **admin** access on the calling repository. This prevents accidental overwrites of production images by non-admin users.

> **Note:** This protection is enforced in the `mosip/kattu` reusable workflow, so it cannot be bypassed by modifying the caller workflow.

**Security Benefits:**
- Tokens are never exposed in workflow logs
- Each organization has isolated credentials
- No hardcoded credentials in workflow files
- Protected organizations require admin access for transfers

### Running the Workflow

1. Go to [Actions → Manual workflow to transfer images](https://github.com/mosip/release-script/actions/workflows/image-transfer.yml)
2. Click "Run workflow"
3. Select branch (usually `master` or `main`)
4. Fill in the required inputs:
   ```
   USERNAME: robot$mosipdev+release-bot
   SECRET_NAME: MOSIPID_DOCKER_TOKEN    (select from dropdown)
   CUSTOM_SECRET_NAME:                  (leave empty unless SECRET_NAME is "custom")
   DESTINATION_ORGANIZATION: mosipid
   REGISTRY_URL: https://harbor.mosip.net
   REGISTRY_TYPE: harbor
   ENABLE_WIREGUARD: true (if registry is on private network)
   ```
5. If using `custom` for `SECRET_NAME`, enter the secret name in `CUSTOM_SECRET_NAME`:
   ```
   SECRET_NAME: custom
   CUSTOM_SECRET_NAME: MY_ORG_DOCKER_TOKEN
   ```
6. Ensure the selected/custom secret is configured under **Settings → Secrets and variables → Actions**
7. Click "Run workflow"

### Workflow Features

✅ **Automated Verification**: Checks source image existence before transfer  
✅ **Multi-Arch Preservation**: Uses Crane to maintain all platform architectures  
✅ **Parallel Processing**: Configurable concurrent transfers (default: 3 workers)  
✅ **VPN Support**: Optional WireGuard for private registry access  
✅ **Detailed Reporting**: Generates transfer report with statistics  
✅ **Slack Notifications**: Sends status updates to configured webhook  
✅ **Git Logging**: Commits transfer logs to repository  

### Workflow Output

The workflow generates a detailed transfer report:

```markdown
# Image Transfer Report

**Date**: Tue Oct 28 12:22:36 UTC 2025
**Registry Type**: harbor
**Registry URL**: https://harbor.mosip.net  
**Organization**: mosipid
**WireGuard VPN**: Enabled

## Statistics
- **Crane transfers**: 16
- **Total completed transfers**: 16
- **Failed transfers**: 0

## Successfully Transferred Images
- mosipdev/kernel-auth-service:1.2.0.1 to mosipid/kernel-auth-service:1.2.0.1
- mosipdev/pre-registration-application-service:1.2.0.1 to mosipid/pre-registration-application-service:1.2.0.1
...
```

## Multi-Architecture Image Support

The tool **automatically handles multi-architecture images** using Crane:

### Example: PostgreSQL 13 (Multi-Arch)

```bash
# Transfer preserves ALL architectures
postgres:13 13
```

**Result**: The transferred image maintains support for:
- `linux/amd64`
- `linux/arm64`
- `linux/arm/v7`
- `linux/ppc64le`
- `linux/s390x`
- And any other architectures from the source

### Verification

```bash
# Check architectures in destination registry
crane manifest your-registry.com/mosipid/postgres:13 | jq '.manifests[] | {arch: .platform.architecture, os: .platform.os}'

# Or using Docker
docker manifest inspect your-registry.com/mosipid/postgres:13
```

## Troubleshooting

### Common Issues

**1. Image Not Found Error**
```
ERROR: Image "postgres:13" does not exist
```
**Solution**: Official Docker Hub images need no `library/` prefix in `images.txt`. Just use `postgres:13 13`.

**2. Crane Not Found**
```
ERROR: crane tool not found
```
**Solution**: Install Crane as shown in Prerequisites section.

**3. Harbor Authentication Failed**
```
Error: unauthorized: authentication required
```
**Solution**: 
- Verify robot account format: `robot$project+name` (not `robot+project`)
- Ensure robot account has push/pull permissions on the project
- Check token is not expired

**4. Registry Connection Timeout**
```
ERROR: Cannot connect to registry
```
**Solution**: 
- For private registries, enable WireGuard VPN (`ENABLE_WIREGUARD: true`)
- Verify registry URL is correct and accessible
- Check firewall rules allow Docker registry ports (typically 443 for HTTPS, 80 for HTTP)

**5. HTTP Registry Issues**
```
ERROR: http: server gave HTTP response to HTTPS client
```
**Solution**: Use `http://` prefix in `registry_url` for insecure registries. The script automatically adds `--insecure` flag for Crane.

### Debug Mode

Enable detailed logging by checking `logs/vidivi.log`:

```bash
tail -f release/vidivi/logs/vidivi.log
```

## Best Practices

1. **Test with `check` first**: Always validate source images before transfer
2. **Use `hash` for verification**: Compare digests when updating existing images
3. **Parallel workers**: Adjust `process.count` based on network bandwidth (recommended: 3-5)
4. **Backup important tags**: Keep copies of production images before overwriting
5. **Monitor transfers**: Watch logs for any warnings or errors
6. **Verify multi-arch**: After transfer, confirm all architectures are present

## Registry Compatibility

| Registry | Tested | Notes |
|----------|--------|-------|
| Docker Hub | ✅ | Fully supported |
| Harbor | ✅ | Requires robot account, VPN optional |
| Azure ACR | ✅ | Use service principal credentials |
| Amazon ECR | ✅ | Use IAM access tokens |
| Google GCR/AR | ✅ | Use service account JSON key |
| GitLab Registry | ✅ | Use deploy tokens |
| GitHub GHCR | ✅ | Use personal access tokens |
| Nexus | ✅ | HTTP/HTTPS both supported |
| Quay.io | ✅ | Use robot account tokens |

## Logs

Transfer logs are stored in:
- `release/vidivi/logs/vidivi.log` - Detailed operation log
- `release/vidivi/transfer_report.md` - Summary report (GitHub Actions only)

## Verification

After transfer, verify images:

```bash
# List transferred images
docker images | grep mosipid

# Pull and test an image
docker pull your-registry.com/mosipid/kernel-auth-service:1.2.0.1
docker run --rm your-registry.com/mosipid/kernel-auth-service:1.2.0.1 --version

# Check image manifest
crane manifest your-registry.com/mosipid/kernel-auth-service:1.2.0.1
```

## License

This tool uses:
- **Crane** (Apache 2.0) - From Google's go-containerregistry project
- **Python Docker SDK** (Apache 2.0)

## Support

For issues or questions:
1. Check `logs/vidivi.log` for detailed error messages
2. Verify configuration in `config.yml`
3. Ensure Crane is installed and accessible
4. Open an issue in the release-script repository

---

**Note**: Source and destination tags in `images.txt` must be **space-separated** on each line.
