#!/bin/bash

set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR/.."

# Source configuration
. etc/config.sh

# Find our external IP. This may take a few minutes
HUBIP=
while [[ -z "$HUBIP" ]]; do
	HUBIP=$(kubectl --namespace="$JHUB_K8S_NAMESPACE" get svc proxy-public --output jsonpath='{.status.loadBalancer.ingress[0].ip}')
	sleep 1
done

# Delete any old DNS entries
DNS_RECORD_IDS=$(doctl compute domain records list $INTERNAL_DOMAIN -o json | jq ".[] | select( .name == \"$HUB_HOSTNAME\") | .id ")
for ID in $DNS_RECORD_IDS; do
	doctl compute domain records delete $INTERNAL_DOMAIN $ID -f
done

# Create a new DNS entry pointing to the external IP
doctl compute domain records create $INTERNAL_DOMAIN --record-type=A --record-name=$HUB_HOSTNAME --record-data=$HUBIP --record-ttl 30
