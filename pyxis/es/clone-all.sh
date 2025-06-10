#!/bin/bash



# Array of repo names
repos=(
  choco-common
  cubie-memory
  data-sql
  device-management
  dispatchr
  dispensing-data-sync
  dispensing-device-health-service
  dispensing-device-services
  dispensing-maintenance-service
  dispensing-shared
  es-database
  es-device-monitor-service
  es-server
  es-station
  es-station-config-utility
  external-comm-service
  external-messaging-contracts
  external-user-directory
  inbound-messaging
  mobile-dock-service
  pharmacy-order-scheduler
  pyxis-common
  pyxis-dispensing-sync
  pyxis-identity-server
  pyxis-link-android
  pyxis-link-api
  pyxis-link-web
  es-system-releases-server
  es-system-releases-station
)

# Clone each repo via SSH
for repo in "${repos[@]}"; do
  echo "Cloning $repo..."
  git clone git@github.com:bd-pyxis/$repo.git
done