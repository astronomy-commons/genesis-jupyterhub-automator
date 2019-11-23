#!/bin/bash

set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR/.."

# Enumerate all config files
VALUES=( $(ls etc/values/*.yaml 2>/dev/null) )
VALUES+=( $(ls etc/images/*/*.yaml 2>/dev/null) )

# Enumerate all secrets
SECRETS=( $(ls etc/secrets/*.yaml 2>/dev/null) )

# Run Helm
set -x
helm upgrade --install $JHUB_HELM_RELEASE \
     jupyterhub/jupyterhub  \
     --namespace "$JHUB_K8S_NAMESPACE" \
     --version="$JHUB_VERSION" \
     ${VALUES[@]/#/--values } \
     ${SECRETS[@]/#/--values } \
     --timeout=800
