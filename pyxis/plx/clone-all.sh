#!/bin/bash

# Base GitHub SSH URL
BASE_SSH_URL="git@github.com:bd-pyxis"

# List of repositories
REPOS=(
  "phg-server"
  "phg-application"
  "phg-system-release"
  "phg-database"
  "phg-migration-utility"
  "phg-archiveandpurge"
  "phg-shared"
  "phg-integrationservice-installer"
  "phg-server-installer"
  "phg-barcode-parser"
  "phg-dependencyinjection"
  "phg-logger"
  "phg-hotfixes"
  "phg-akka"
  "phg-label-designer"
  "phg-invoice-tool"
  "emr-interop"
  "cost-update-service"
  "phg-scancodexrefextractionservice"
  "phg-pci-tools"
)

# Clone each repository
for repo in "${REPOS[@]}"; do
  echo "Cloning $repo..."
  echo "$BASE_SSH_URL/$repo.git"
  git clone "$BASE_SSH_URL/$repo.git"
done

echo "✅ Done cloning all repositories (via SSH)."