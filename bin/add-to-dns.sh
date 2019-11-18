#!/bin/bash

set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR/.."

HOST=$(echo $HUB_FQDN | cut -d . -f 1)
DOMAIN=$(echo $HUB_FQDN | cut -d . -f 2-)

# Find our external IP. This may take a few minutes
HUBIP=
while [[ -z "$HUBIP" ]]; do
	HUBIP=$(kubectl --namespace="$JHUB_K8S_NAMESPACE" get svc proxy-public --output jsonpath='{.status.loadBalancer.ingress[0].ip}')
	sleep 1
done

# See if we already have the correct entry, skip if so
CURIP=$(doctl compute domain records list alerts.wtf -o json | jq -r ".[] | select( .name == \"hub\") | .data")
if [[ "$CURIP" == "$HUBIP" ]]; then
	echo "DNS for $HUB_FQDN already points to the correct IP ($CURIP)."
	exit
fi

# Delete any old DNS entries
DNS_RECORD_IDS=$(doctl compute domain records list $DOMAIN -o json | jq ".[] | select( .name == \"$HOST\") | .id ")
for ID in $DNS_RECORD_IDS; do
	doctl compute domain records delete $DOMAIN $ID -f
done

# Create a new DNS entry pointing to the external IP
doctl compute domain records create $DOMAIN --record-type=A --record-name=$HOST --record-data=$HUBIP --record-ttl 30
