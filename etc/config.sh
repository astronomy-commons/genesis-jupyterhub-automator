# Kubernetes cluster creation definitions. Modify and then source this before
# following the instructions in the README.md

CLUSTER_NAME=genesis
K8S_VERSION=1.15.5-do.1
SIZE=s-4vcpu-8gb
NODES=3
NODE_POOL_NAME=$SIZE
REGION=sfo2
CONTEXT=do-$REGION-$CLUSTER_NAME

# JupyterHub hostname and domains
HUB_HOSTNAME=hub
EXTERNAL_DOMAIN=alerts.wtf
INTERNAL_DOMAIN=do.alerts.wtf
FQDN=$HUB_HOSTNAME.$EXTERNAL_DOMAIN

# JupyterHub to install, and kubernetes namespace to install it into
JHUB_VERSION=0.9.0-alpha.1.028.00bc15c
JHUB_HELM_RELEASE=genesis-jhub
JHUB_K8S_NAMESPACE=genesis

# Let's Encrypt SSL cerfiticates information
EMAIL=email@example.com
