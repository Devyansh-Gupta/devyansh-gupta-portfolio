#!/usr/bin/env bash
# Deploy Devyansh Gupta portfolio to Azure Static Web Apps
# Run after: az login
set -euo pipefail

RG="rg-devyansh-portfolio"
LOC="centralindia"
SWA="swa-devyansh-portfolio"

echo "==> resource group"
az group create --name "$RG" --location "$LOC" --output none

echo "==> static web app (manual deployment mode; GitHub Actions wired after)"
az staticwebapp create --name "$SWA" --resource-group "$RG" --location "$LOC" \
  --sku Free --no-wait 2>/dev/null || true

echo "==> app settings (secrets)"
az staticwebapp appsettings set --name "$SWA" --setting-names \
  "SMTP_HOST=${SMTP_HOST:-smtp.gmail.com}" \
  "SMTP_PORT=${SMTP_PORT:-587}" \
  "SMTP_USER=${SMTP_USER:-devyanshgupta04@gmail.com}" \
  "SMTP_PASS=${SMTP_PASS:-SET_ME}" \
  "CONTACT_TO=${CONTACT_TO:-devyanshgupta04@gmail.com}"

echo "==> deploy static content + api"
az staticwebapp deploy --name "$SWA" --source . --app-location "/" \
  --api-location "api" --output-location "/" --no-build true

echo "==> done"
az staticwebapp show --name "$SWA" --query "defaultHostname" --output tsv
