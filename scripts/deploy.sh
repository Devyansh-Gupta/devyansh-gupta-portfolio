#!/usr/bin/env bash
# Deploy Devyansh Gupta portfolio to Azure Static Web Apps + Blob Storage
# Run after: az login
set -euo pipefail

RG="rg-devyansh-portfolio"
LOC="centralindia"
SWA="swa-devyansh-portfolio"
STORAGE="stdevyanshportfolio"
CONTAINER="resume"
BLOB="Devyansh_Gupta_Resume_DevOps_Intern.pdf"
REPO="https://github.com/Devyansh-Gupta/devyansh-gupta-portfolio"
BRANCH="main"

echo "==> resource group"
az group create --name "$RG" --location "$LOC" --output none

echo "==> storage account"
az storage account create --name "$STORAGE" --resource-group "$RG" \
  --location "$LOC" --sku Standard_LRS --allow-blob-public-access false \
  --https-only true --output none

echo "==> private container + resume blob"
az storage container create --name "$CONTAINER" --account-name "$STORAGE" \
  --public-access off --auth-mode login --output none
az storage blob upload --account-name "$STORAGE" --container-name "$CONTAINER" \
  --name "$BLOB" --file "assets/$BLOB" --overwrite --auth-mode login --output none

echo "==> static web app (manual deployment mode; GitHub Actions wired after)"
az staticwebapp create --name "$SWA" --resource-group "$RG" --location "$LOC" \
  --sku Free --no-wait 2>/dev/null || true

echo "==> app settings (secrets)"
KEY=$(az storage account keys list --account-name "$STORAGE" --resource-group "$RG" \
  --query "[0].value" --output tsv)

az staticwebapp appsettings set --name "$SWA" --setting-names \
  "STORAGE_ACCOUNT=$STORAGE" \
  "STORAGE_KEY=$KEY" \
  "RESUME_CONTAINER=$CONTAINER" \
  "RESUME_BLOB=$BLOB" \
  "RESUME_SAS_MINUTES=10" \
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
