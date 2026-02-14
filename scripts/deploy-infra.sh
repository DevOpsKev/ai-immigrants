#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

RESOURCE_GROUP="${1:?Usage: $0 <resource-group-name>}"
TEMPLATE="$REPO_ROOT/infra/main.bicep"
PARAMS="$REPO_ROOT/infra/main.bicepparam.json"

echo "==> Deploying infrastructure to resource group: $RESOURCE_GROUP"

az deployment group create \
  --resource-group "$RESOURCE_GROUP" \
  --template-file "$TEMPLATE" \
  --parameters "@$PARAMS" \
  --output table

echo "==> Done."
echo ""
echo "Download URL:"
az deployment group show \
  --resource-group "$RESOURCE_GROUP" \
  --name main \
  --query "properties.outputs.downloadUrl.value" \
  --output tsv