# Standing up a Genesis Platform instance on Digital Ocean Kubernetes

This is a very condensed summary of how to create an instance of the Genesis
JupyterHub platform on Digital Ocean. If you're new to JupyterHub on
Kubernetes,
[zero-to-jupyterhub](https://zero-to-jupyterhub.readthedocs.io/en/latest/)
is a stongly suggested supplemental reading.

## Prerequisites

Assuming you're on a Mac an using brew, install the necessary packages with:
```
brew install doctl
brew install kubernetes-cli
brew install kubernetes-helm
brew install certbot
```

Initialize Digital Ocean authentication:
```
doctl auth init
```
This will ask you for your DO API token, which you can get from the DO
website.

## Configuration

Edit the high-level configuration file `config.sh`, then source it:
```
. etc/config.sh
```
Note: to find out what node types are available for setting `SIZE` parameter in `config.sh`
(the "slugs"), run `doctl compute size list`.


## Create a Kubernetes Cluster

This sets up a kubernetes cluster with Helm and the web dashboard:
```
# Create cluster. This may take ~10 minutes to execute on DO
doctl k8s cluster create $CLUSTER_NAME --region $REGION --node-pool="name=$NODE_POOL_NAME;size=$SIZE;count=$NODES" --version=$K8S_VERSION

# Switch the context to the cluster we just created, so future commands apply to it:
kubectl config use-context $CONTEXT

# Install Helm (tiller)
kubectl --namespace kube-system create serviceaccount tiller
kubectl create clusterrolebinding tiller --clusterrole cluster-admin --serviceaccount=kube-system:tiller
helm init --service-account tiller --wait
kubectl patch deployment tiller-deploy --namespace=kube-system --type=json \
  --patch='[{"op": "add", "path": "/spec/template/spec/containers/0/command", "value": ["/tiller", "--listen=localhost:44134"]}]'
```

### Optional: Add the Dashboard GUI

```
# Set up k8s web dashboard (check for new versions at https://github.com/kubernetes/dashboard/releases)
kubectl delete ns kubernetes-dashboard # this will err if you're installing for the first time; that's OK.
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.0.0-beta6/aio/deploy/recommended.yaml

# Set up an admin user, and get their secret token which we'll use to access the web interface
kubectl apply -f deploy/create-dashboard-admin-user.yaml
kubectl -n kubernetes-dashboard describe secret $(kubectl -n kubernetes-dashboard get secret | grep admin-user | awk '{print $1}') | grep -E '^token:'
kubectl proxy &

# then go to http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/#/login to access the dashboard
# with the token you just generated.
```

## Install JupyterHub

```
# Install JupyterHub helm repository
helm repo add jupyterhub https://jupyterhub.github.io/helm-chart/
helm repo update

# Generate the secret internal JupyterHub proxy communication token
mkdir -p secrets
cat > secrets/proxy.yaml <<-EOF
proxy:
  secretToken: "$(openssl rand -hex 32)"
EOF

# Install JupyterHub
# This may take a couple of minutes, as the Docker images are being pre-pulled
# into every node in the Kubernetes namespace
helm upgrade --install $JHUB_HELM_RELEASE jupyterhub/jupyterhub \
     --namespace "$JHUB_K8S_NAMESPACE" --version="$JHUB_VERSION" \
     --values etc/values.yaml --values secrets/proxy.yaml --timeout=800

# Find our external IP. This may take a few minutes
HUBIP=
while [[ -z "$HUBIP" ]]; do
	HUBIP=$(kubectl --namespace="$JHUB_K8S_NAMESPACE" get svc proxy-public --output jsonpath='{.status.loadBalancer.ingress[0].ip}')
	sleep 1
done

# Create a new DNS entry pointing to the external API (delete any old ones)
DNS_RECORD_IDS=$(doctl compute domain records list $INTERNAL_DOMAIN -o json | jq ".[] | select( .name == \"$HUB_HOSTNAME\") | .id ")
for ID in $DNS_RECORD_IDS; do
	doctl compute domain records delete $INTERNAL_DOMAIN $ID -f
done
doctl compute domain records create $INTERNAL_DOMAIN --record-type=A --record-name=$HUB_HOSTNAME --record-data=$HUBIP --record-ttl 30

# At this point you should be able to access JupyterHub via http://$FQDN
curl -L http://$FQDN
```

## Setting up SSL

Manual setup, while automatics are broken (see https://github.com/jupyterhub/zero-to-jupyterhub-k8s/issues/1448).
You'll have to follow the `certbot` instructions on how to manually add a TXT record to your domain config.

Note: this won't work with JupyterHub < 0.9.0-alpha.1.028.00bc15c -- see
https://github.com/jupyterhub/zero-to-jupyterhub-k8s/issues/806 -- which is
why we're using this version (rather than the stable one).

```
## Pass the certbot challenge to get the certificates
mkdir -p secrets/certbot/{config,logs,work}
certbot -d "$FQDN" --manual --preferred-challenges dns certonly --config-dir secrets/certbot/config --work-dir secrets/certbot/work --logs-dir secrets/certbot/logs -m "$EMAIL" --agree-tos

## Copy new certs into a yaml file
cat > secrets/https.yaml <<-EOF
proxy:
  https:
    hosts:
      - $FQDN
    type: manual
    manual:
      key: |
$(cat secrets/certbot/config/live/$FQDN/privkey.pem |  sed 's/^/        /')
      cert: |
$(cat secrets/certbot/config/live/$FQDN/fullchain.pem |  sed 's/^/        /')
EOF

## Redeploy with https turned on
helm upgrade --install $JHUB_HELM_RELEASE jupyterhub/jupyterhub \
     --namespace "$JHUB_K8S_NAMESPACE" --version="$JHUB_VERSION" \
     --values etc/values.yaml --values secrets/proxy.yaml --values secrets/https.yaml --timeout=800
```

## Optional: GitHub Authentication

To set up GitHub authentication, copy `secrets/auth.yaml.example` to
`secrets/auth.yaml` and follow the instructions at
[zero-to-jupyterhub](https://zero-to-jupyterhub.readthedocs.io/en/latest/authentication.html#github)
website.

## Deleting everything

```
helm delete $JHUB_HELM_RELEASE --purge
kubectl delete namespace "$JHUB_K8S_NAMESPACE"
doctl k8s cluster delete $CLUSTER_NAME
```

## Useful commands

```
kubectl get pod --namespace $JHUB_K8S_NAMESPACE
kubectl get service --namespace $JHUB_K8S_NAMESPACE
kubectl get pvc --namespace $JHUB_K8S_NAMESPACE
```
