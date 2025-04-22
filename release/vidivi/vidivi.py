name: Deploy External services of mosip using Helmsman

on:
  workflow_dispatch:
    inputs:
      mode:
        description: "Choose Helmsman mode: dry-run or apply"
        required: true
        default: "dry-run"
        type: choice
        options:
          - dry-run
          - apply       
  push:
    paths:
      - deployment/v3/helmsman/dsf/*

jobs:
  determine-changes:
    runs-on: ubuntu-latest
    outputs:
      prereq_needed: ${{ steps.check-changes.outputs.prereq_needed }}
      external_needed: ${{ steps.check-changes.outputs.external_needed }}
      mosip_needed: ${{ steps.check-changes.outputs.mosip_needed }}
    steps:
      - name: Checkout repository with full history
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Get full commit history

      - name: Check changed files
        id: check-changes
        run: |
          # Default to true for workflow_dispatch
          prereq_needed="false"
          external_needed="false" 
          mosip_needed="false"
          
          if [[ "$GITHUB_EVENT_NAME" == "workflow_dispatch" ]]; then
            prereq_needed="true"
            external_needed="true"
            mosip_needed="true"
          else
            # Handle different event types properly
            if [[ "$GITHUB_EVENT_NAME" == "push" ]]; then
              # For push events, use GitHub's provided SHAs
              base_sha="${{ github.event.before}}"
              head_sha="${{ github.sha }}"
            elif [[ "$GITHUB_EVENT_NAME" == "pull_request" ]]; then
              # For PRs, compare against target branch
              base_sha="${{ github.event.pull_request.base.sha }}"
              head_sha="${{ github.event.pull_request.head.sha }}"
            fi

            # Get changed files safely
            changed_files=$(git diff --name-only "$base_sha" "$head_sha" -- 'deployment/v3/helmsman/dsf/' || echo "")
            
            # Check each specific file
            if echo "$changed_files" | grep -qx 'deployment/v3/helmsman/dsf/prereq-dsf.yaml'; then
              prereq_needed="true"
            fi
      
            if echo "$changed_files" | grep -qx 'deployment/v3/helmsman/dsf/external-dsf.yaml'; then
              external_needed="true"
            fi

            if echo "$changed_files" | grep -qx 'deployment/v3/helmsman/dsf/mosip-dsf.yaml'; then
              mosip_needed="true"
            fi
          fi

          echo "prereq_needed=$prereq_needed" >> $GITHUB_OUTPUT
          echo "external_needed=$external_needed" >> $GITHUB_OUTPUT
          echo "mosip_needed=$mosip_needed" >> $GITHUB_OUTPUT

  deploy-prereq-dsf:
    runs-on: ubuntu-latest
    needs: determine-changes
    if: needs.determine-changes.outputs.prereq_needed == 'true'
    steps:
      - name: Checkout repository
        uses: actions/checkout@v2

      - name: Deploy prereq DSF
        uses: ./.github/actions/dsf-deploy
        with:
          dsf_file: prereq-dsf.yaml
          wg_conf: wg0
          mode: ${{ github.event.inputs.mode }}
          kubeconfig: ${{ secrets.KUBECONFIG }}
          wireguard_wg0: ${{ secrets.CLUSTER_WIREGUARD_WG0 }}
          wireguard_wg1: ${{ secrets.CLUSTER_WIREGUARD_WG1 }}
          wireguard_wg2: ${{ secrets.CLUSTER_WIREGUARD_WG2 }}

  deploy-external-dsf:
    runs-on: ubuntu-latest
    needs: determine-changes
    if: needs.determine-changes.outputs.external_needed == 'true'
    steps:
      - name: Checkout repository
        uses: actions/checkout@v2

      - name: Deploy external DSF
        uses: ./.github/actions/dsf-deploy
        with:
          dsf_file: external-dsf.yaml
          wg_conf: wg1
          mode: ${{ github.event.inputs.mode }}
          kubeconfig: ${{ secrets.KUBECONFIG }}
          wireguard_wg0: ${{ secrets.CLUSTER_WIREGUARD_WG0 }}
          wireguard_wg1: ${{ secrets.CLUSTER_WIREGUARD_WG1 }}
          wireguard_wg2: ${{ secrets.CLUSTER_WIREGUARD_WG2 }}

  deploy-mosip-dsf:
    runs-on: ubuntu-latest
    needs: [determine-changes, deploy-prereq-dsf, deploy-external-dsf]
    if: needs.determine-changes.outputs.mosip_needed == 'true'
    steps:
      - name: Checkout repository
        uses: actions/checkout@v2

      - name: Deploy MOSIP DSF
        uses: ./.github/actions/dsf-deploy
        with:
          dsf_file: mosip-dsf.yaml
          wg_conf: wg2
          mode: ${{ github.event.inputs.mode }}
          kubeconfig: ${{ secrets.KUBECONFIG }}
          wireguard_wg0: ${{ secrets.CLUSTER_WIREGUARD_WG0 }}
          wireguard_wg1: ${{ secrets.CLUSTER_WIREGUARD_WG1 }}
          wireguard_wg2: ${{ secrets.CLUSTER_WIREGUARD_WG2 }}
