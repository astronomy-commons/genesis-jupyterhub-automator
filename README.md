# Genesis JupyterHub Deployment Repository

This is a very condensed summary of how to create an instance of the Genesis
JupyterHub on [Digital Ocean](https://www.digitalocean.com/). Genesis
JupyterHub is a distribution of JupyterHub with a Jupyter image containing:

* Astronomy event streaming clients (`genesis.streaming`)
* Tools for scalable queries of data in cloud-based data lakes (TBD)
* Numerous preinstalled astronomy/astrophysics packages.

This repository contains:
* Instructions to create a Kubernetes cluster on DigitalOcean
* Helm charts and pre-made configs to install the JupyterHub onto a Kubernetes cluster.
* Dockerfiles for customized JupyterHub and Jupyter images

If you're new to JupyterHub on Kubernetes,
[zero-to-jupyterhub](https://zero-to-jupyterhub.readthedocs.io/en/latest/)
is a stongly suggested supplemental reading.

## Prerequisites

To set this up, you'll need:
* A Digital Ocean ("DO") account
* Command line utilities for DO and kubernetes

Assuming you're on a Mac an using brew, you can install the necessary packages with:
```
brew install doctl
brew install kubernetes-cli
brew install kubernetes-helm
brew install certbot
```

Then authenticate against Digital Ocean by running:
```
doctl auth init
```
This will ask you for your DO Personal Access token, [which you can manage
and create here](https://cloud.digitalocean.com/account/api/tokens).

## Configuration

Run:
```
./configure --provider=do --hub-fqdn=<hub.example.com> \
            --github-oauth-client-id=.... --github-oauth-secret=.... \
            --letsencrypt-email=<me@example.com>
```

This will generate configuration in `etc/`. Most of it resides in two key files:
* `etc/Makefile.config`: Kubernetes cluster and high-level JupyterHub definitions
* `etc/values.yaml`: JupyterHub customizations
Edit and customize them as necessary.

Note: to find out what node types are available for setting `SIZE` parameter in `config.sh`
(the "slugs"), run `doctl compute size list`.

## Deployment

To deploy JupyterHub, run:

```
make
```

This will:
* Create a new Kubernetes cluster, if needed
* Installs Helm, if needed
* Installs Dashboard, if needed
* Installs JupyterHub with Genesis customizations

## Deleting everything

Run:
```
make destroy
```

## Useful commands

```
kubectl get pod --namespace $JHUB_K8S_NAMESPACE
kubectl get service --namespace $JHUB_K8S_NAMESPACE
kubectl get pvc --namespace $JHUB_K8S_NAMESPACE
```
