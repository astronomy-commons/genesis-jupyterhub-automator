# JupyterHub Deployment Automator

The tools in this repository automates the process of creating an instance
of JupyterHub on [Digital Ocean](https://www.digitalocean.com/)'s managed
Kubernetes (a.k.a.  k8s) instance.  We primarily aim to simplify the
deployment of one-off JupyterHubs for events -- demos, tutorials, or even
classes.

This is largely an automation of the process described at
[zero-to-jupyterhub](https://zero-to-jupyterhub.readthedocs.io/en/latest/);
we strongly recommend reading that excellent guide to understand the config
files this automator generates.  That said our goal is to make deployment
possible even if you're not intimately familiar with Kubernetes or
JupyterHub: if the defaults work for you, this code and document may be all
you need.


## What Do You Get?

The automator creates and deploys a JupyterHub instance with presets as
follows in its default configuration:
* Running on Digital Ocean's managed Kubernetes instance (it will create one
  for you). Your users will access it from a custom URL such as
  https://hub.alerts.wtf.
* The cluster consists of three 4-core, 8 GB RAM virtual machines. By
  default, we allocate one machine per user, and the users' sessions are shut 
  down after 1hr of inactivity (all of this can be customized).
* Default software environment includes Python 2.7, 3, and R, with a suite
  of "usual" data science and astronomy software pre-installed (e.g.,
  astropy). There are options to customize it.
* The hub will pull a repository of your own choice to any user's directory,
  suitable for distribution of demo materials.
* The users authenticate with GitHub accounts, allowing either any GitHub user to log in, or just
  members of a particular organization(s).
* All communications are secured with SSL (i.e., https://)

To deploy JupyterHub you'll need:
1. A [Digital Ocean](https://www.digitalocean.com/) ("DO") account.
1. Command line utilities for DO (`doctl`) and Kubernetes (`kubectl`).
1. A domain you own, where your hub will reside (e.g., `alerts.wtf` if your hub is to
   be at `hub.alerts.wtf`), which must be managed by [Digital Ocean's DNS
   service](https://www.digitalocean.com/community/tutorials/how-to-point-to-digitalocean-nameservers-from-common-domain-registrars).
1. A registered [GitHub OAuth app](https://developer.github.com/apps/building-oauth-apps/creating-an-oauth-app/), to represent your deployment.
   See [here](https://zero-to-jupyterhub.readthedocs.io/en/latest/administrator/authentication.html#authenticating-with-oauth2) for 
   details on how to create one.

The `./configure` script included here will try to check you have all of the
above, before allowing you to proceed.


## Installing: Zero-to-JupyterHub in 10-30 minutes

In the example below, we assume:
* you own (or plan to buy) a domain named `alerts.wtf`, and your JupyterHub
  will reside at `https://hub.alerts.wtf`
* your e-mail is `kathryn.janeway@uw.edu`

Replace these with your actual domain name, host name, and e-mail.

### 1. Install required command line utilities

Assuming you're on a Mac and using [Homebrew](http://brew.sh), installing is
as simple as:
```
brew install doctl
brew install kubernetes-cli
brew install kubernetes-helm
brew install certbot
```

### 2. Create or log into your Digital Ocean account

Go to [Digital Ocean](https://www.digitalocean.com/), open an account, and
remain logged in on the website.

Then authenticate via the command-line tools by running:
```
doctl auth init
```
This will ask you for your "Personal Access Token", an analog of your
username/password when using command line tools. You create a new token
at the [personal access token page](https://cloud.digitalocean.com/account/api/tokens).

### 3. Purchase a domain, have Digital Ocean DNS manage it

If you don't already own a domain, purchase it from one of the [many domain name
registers out
there](https://www.techradar.com/news/best-domain-registrars-in-2019). If
confused about which one to choose, try [namecheap.com](https://www.namecheap.com/)
-- we've had good experiences wth it.

Then follow [Digital Ocean's instructions](https://www.digitalocean.com/community/tutorials/how-to-point-to-digitalocean-nameservers-from-common-domain-registrars)
to transfer the DNS management to Digital Ocean.

### 4. Create a GitHub OAuth Application

Next, follow the [instructions on GitHub](https://developer.github.com/apps/building-oauth-apps/creating-an-oauth-app/)
to register a new "OAuth Application". In layman terms, this is how GitHub
will identify your JupyterHub and know to allow users to log into it using
their GitHub credentials.

The most important field in the form is the one named 'Authorization
callback URL'. Make sure you set it equal to
`https://hub.alerts.wtf/hub/oauth_callback`, where `hub.alerts.wtf` is
will be the hostname of the JupyterHub you'll be standing up. You should use
the same hostname in the 'Homepage URL' field (but with 'https://'
prepended).

After you've created the app, jot down the values of the generated 'Client
ID' (a 20-characters string) and 'Client Secret' (a 40-character string)
fields. You'll need these two in the next step.

### 5. Configure your JupterHub

This repository comes with a ./configure script that automates the tedious
work of generating of all the required configuration files.

Having done the prep work above, run:
```
./configure --provider=do \
            --hub-fqdn=hub.alerts.wtf \
            --github-oauth-client-id=<20-char-string-from-step-4> \
            --github-oauth-secret=<40-char-string-from-step-4> \
            --letsencrypt-email=kathryn.janeway@uw.edu
```

This will generate configuration for you JupyterHub in `etc/`.

### 6. Deploy

You're now ready to deploy it by running:

```
make all
```

If everything works out as it's supposed to, in about ~10 minutes your
JupyterHub will be ready at https://hub.alerts.wtf.

If not, [open an issue
here](https://github.com/dirac-institute/genesis-platform/issues), and make
sure to include as much of the error messages, logs, or other relevant
information.

## Deleting everything

Once you're done, make sure to clean up after yourself (otherwise your
cluster will keep accruing charges).

To destroy ***everything*** that was created (both JupyterHub and the Kubernetes
cluster), run:

```
make destroy
```

WARNING: This is irreversible!  All data residing in the deployment (e.g.,
new or modified notebooks) will be lost.

## About Cost (good news: it's not huge!)

Deploying in the cloud for the first time can be stressful because of fears
about cost. For short term-deployment, the costs can be fairly low.

### Example 1: Daily cost of default deployment

The daily cost for the default deployment (3 nodes) assuming 10 active users
(and using pricing as of Nov 18th, 2019):

* Worker nodes: $0.06/hr/node * 10nodes * 24hrs = $4.32/day
* User storage: $0.0015/hr/GB * 1GB/user * 10users * 24hrs = $0.36/day

* Total: $4.68/day

This gives you a sense for how much you'll pay while testing/developing a
deployment.

### Example 2: Running a short tutorial

Running a 3-hr, 50-person, tutorial: (0.06 + 0.0015)*50*3 = $9.225

### Example 3: Running a 5-week workshop

Running a 5-day, 25-person workshop: (0.06 + 0.0015)*25*24*5 = $184.5

Add to these the yearly cost of purchasing a domain (typically $10-20/yr).

Costs can change (in either direction) by choosing a different node type or
a different amount of per-user storage. See https://www.digitalocean.com/pricing/
for options and current pricing.

## Details

### Customizing your Deployment

Many customizations can be made via command-line arguments to `./configure`.
To discover what's available, run:

```
./configure --help
```

Configure generates configuration files in the `etc/` subdirectory. Among
other things, this directory contains:
* `etc/Makefile.config`: Kubernetes cluster and high-level JupyterHub definitions
* `etc/values.yaml`: JupyterHub customizations
* `etc/secrets/*`: deployment customizations which should never be made
  public (contains private keys, tokens, etc.)

You can edit and customize it as you see fit, and run `make deploy` to have
the changes take effect.

### Useful Kubernets commands

```
kubectl get pod --namespace $JHUB_K8S_NAMESPACE
kubectl get service --namespace $JHUB_K8S_NAMESPACE
kubectl get pvc --namespace $JHUB_K8S_NAMESPACE
```

### Future Work

* Document ./configure options and available customizations
* Switch back to automatic SSL certificate management once
  [#1448](https://github.com/jupyterhub/zero-to-jupyterhub-k8s/issues/1448) is fixed
* Record a video tutorial on setting up JupyterHub
* Add other cloud providers (starting with AWS)
