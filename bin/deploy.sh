#!/bin/bash

set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR/.."

set -x

# Enumerate all secrets
SECRETS=( $(ls etc/secrets/*.yaml 2>/dev/null) )

# Run Helm
helm upgrade --install $JHUB_HELM_RELEASE \
     jupyterhub/jupyterhub  \
     --namespace "$JHUB_K8S_NAMESPACE" \
     --version="$JHUB_VERSION" \
     --values etc/values.yaml \
     ${SECRETS[@]/#/--values } \
     --timeout=800
