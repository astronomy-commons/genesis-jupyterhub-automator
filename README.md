# Genesis JupyterHub Deployment

The code in this repository automates the process of creating an instance
of Genesis-customized JupyterHub on [Digital Ocean](https://www.digitalocean.com/).
It is largely an automation of the process described at
[zero-to-jupyterhub](https://zero-to-jupyterhub.readthedocs.io/en/latest/).
We strongly recommend referring to that link to understand what the scripts
supplied here do.

This repository contains:
* A `./configure` script which will generate the necessary config files and
  Helm customizations enabling us to:
  * create a Kubernetes cluster on Digital Ocean
  * deploy JupyterHub onto that cluster
  * set up authentication with GitHub
  * set up SSL with Let's Encrypt
* A `Makefile` which does the above in an automated fashon
* Dockerfiles for Genesis-customized JupyterHub and Jupyter images

Genesis JupyterHub is a distribution of JupyterHub with a Jupyter image containing:

* Astronomy event streaming clients (`genesis.streaming`)
* Tools for scalable queries of data in cloud-based data lakes (TBD)
* Numerous preinstalled astronomy/astrophysics packages.

## Prerequisites

To set this up, you'll need:
1. A Digital Ocean ("DO") account
1. Command line utilities for DO and Kubernetes (more below)
1. A domain where your hub will reside (e.g., `example.com` if your hub is to
   be at `hub.example.com`), which must be managed by [Digital Ocean's DNS
   service](https://www.digitalocean.com/community/tutorials/how-to-point-to-digitalocean-nameservers-from-common-domain-registrars).
1. A registered [GitHub OAuth app](https://developer.github.com/apps/building-oauth-apps/creating-an-oauth-app/), to represent your deployment.
   See [here](https://zero-to-jupyterhub.readthedocs.io/en/latest/administrator/authentication.html#authenticating-with-oauth2) for 
   details on how to create one.

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

Think of this as a starting point for your deployment -- edit and customize the
generated scripts as you see fit.

Note: to find out what node types are available for setting `SIZE` parameter in `config.sh`
(the "slugs"), run `doctl compute size list`.

## Deployment

To deploy JupyterHub, run:

```
make
```

This will:
* Create a new Kubernetes cluster, if needed
* Install Helm, if needed
* Install Kubernetes Dashboard, if needed
* Install JupyterHub with Genesis customizations

Once the process finishes, your JupyterHub will be accessible at
http://hub.example.com (or the domain you've set up).

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
