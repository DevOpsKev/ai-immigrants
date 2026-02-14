#!/usr/bin/env bash
set -euo pipefail

echo "==> Installing Azure CLI..."

# Add Microsoft signing key and repo
sudo mkdir -p /etc/apt/keyrings
curl -sLS https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | sudo tee /etc/apt/keyrings/microsoft.gpg > /dev/null
sudo chmod go+r /etc/apt/keyrings/microsoft.gpg

AZ_DIST=$(lsb_release -cs)
echo "Types: deb
URIs: https://packages.microsoft.com/repos/azure-cli/
Suites: ${AZ_DIST}
Components: main
Architectures: $(dpkg --print-architecture)
Signed-by: /etc/apt/keyrings/microsoft.gpg" | sudo tee /etc/apt/sources.list.d/azure-cli.sources > /dev/null

# Install from Microsoft repo only, skip broken third-party repos
sudo apt-get update -o Dir::Etc::sourcelist="sources.list.d/azure-cli.sources" -o Dir::Etc::sourceparts="-" -o APT::Get::List-Cleanup="0" -qq
sudo apt-get install -y -qq azure-cli > /dev/null

echo "==> Verifying..."
az version --output table

echo "==> Done. Run 'az login' to authenticate."