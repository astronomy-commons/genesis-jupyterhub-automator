#!/bin/bash

set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR/.."

[[ -z "$CERTBOT_VALIDATION" ]] && { echo "error: this script is designed to run through 'certbot ... --manual-auth-hook=$0' (\$CERTBOT_VALIDATION is not set)."; exit -1; }
[[ -z "$CERTBOT_DOMAIN" ]] && { echo "error: this script is designed to run through 'certbot ... --manual-auth-hook=$0' (\$CERTBOT_DOMAIN is not set)."; exit -1; }

HOST=_acme-challenge.$(echo "$CERTBOT_DOMAIN" | cut -d . -f 1)
DOMAIN=$(echo "$CERTBOT_DOMAIN" | cut -d . -f 2-)

# Delete any old entries
DNS_RECORD_IDS=$(doctl compute domain records list $DOMAIN -o json | jq ".[] | select( .name == \"$HOST\") | .id ")
for ID in $DNS_RECORD_IDS; do
	doctl compute domain records delete $DOMAIN $ID -f
done

doctl compute domain records create $DOMAIN --record-type=TXT --record-name=$HOST --record-data=$CERTBOT_VALIDATION --record-ttl 30
