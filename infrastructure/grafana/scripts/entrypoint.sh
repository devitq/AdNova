#!/bin/sh

set -e

echo "Installing Grafana plugins..."
grafana cli plugins install yesoreyeram-infinity-datasource

echo "Starting Grafana..."
exec /run.sh
