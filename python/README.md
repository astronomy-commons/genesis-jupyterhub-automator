# usage

The automator has four commands: `init`, `deploy`, `edit`, and `delete`:
```
python automator.py --help
```
```
usage: automator.py [-h] {init,deploy,edit,delete} ...

JupyterHub on Kubernetes Automator

positional arguments:
  {init,deploy,edit,delete}
    init                Initialize a deployment
    deploy              Deploy a deployment
    edit                Edit a part of a deployment
    delete              Delete a deployment in whole or in part

optional arguments:
  -h, --help            show this help message and exit
```

# init
`init` creates a directory containing the "state" of a JupyterHub on Kubernetes deployment.
```
python automator.py init --help
```
```
usage: automator.py init [-h] --provider PROVIDER [--k8s-version K8S_VERSION]
                         [--cluster-name CLUSTER_NAME] [--region REGION]
                         [--availability-zones AVAILABILITY_ZONES [AVAILABILITY_ZONES ...]]
                         [--size SIZE] [--nodes NODES]
                         [--nodegroup-name NODEGROUP_NAME]
                         [--nodegroup-availability-zones NODEGROUP_AVAILABILITY_ZONES [NODEGROUP_AVAILABILITY_ZONES ...]]
                         [--hub-chart-repository HUB_CHART_REPOSITORY]
                         [--hub-chart-name HUB_CHART_NAME]
                         [--hub-chart-version HUB_CHART_VERSION]
                         [--hub-image HUB_IMAGE]
                         [--hub-namespace HUB_NAMESPACE]
                         [--hub-release-name HUB_RELEASE_NAME]
                         [--hub-values HUB_VALUES [HUB_VALUES ...]]
                         [--hub-admin-user HUB_ADMIN_USER] [--cpu CPU]
                         [--memory MEMORY] [--storage STORAGE]
                         [--notebook-image NOTEBOOK_IMAGE]
                         [--notebook-start-scripts NOTEBOOK_START_SCRIPTS [NOTEBOOK_START_SCRIPTS ...]]
                         [--domain-name DOMAIN_NAME]
                         [--dns-provider DNS_PROVIDER]
                         [--eksctl-api-version EKSCTL_API_VERSION]
                         [--dashboard-version DASHBOARD_VERSION]
                         deployment

positional arguments:
  deployment            The deployment directory.

optional arguments:
  -h, --help            show this help message and exit
  --provider PROVIDER
  --k8s-version K8S_VERSION
                        The Kubernetes Version to use.
  --cluster-name CLUSTER_NAME
  --region REGION
  --availability-zones AVAILABILITY_ZONES [AVAILABILITY_ZONES ...]
  --size SIZE
  --nodes NODES
  --nodegroup-name NODEGROUP_NAME
  --nodegroup-availability-zones NODEGROUP_AVAILABILITY_ZONES [NODEGROUP_AVAILABILITY_ZONES ...]
  --hub-chart-repository HUB_CHART_REPOSITORY
  --hub-chart-name HUB_CHART_NAME
  --hub-chart-version HUB_CHART_VERSION
  --hub-image HUB_IMAGE
  --hub-namespace HUB_NAMESPACE
  --hub-release-name HUB_RELEASE_NAME
  --hub-values HUB_VALUES [HUB_VALUES ...]
  --hub-admin-user HUB_ADMIN_USER
  --cpu CPU
  --memory MEMORY
  --storage STORAGE
  --notebook-image NOTEBOOK_IMAGE
  --notebook-start-scripts NOTEBOOK_START_SCRIPTS [NOTEBOOK_START_SCRIPTS ...]
  --domain-name DOMAIN_NAME
  --dns-provider DNS_PROVIDER
  --eksctl-api-version EKSCTL_API_VERSION
  --dashboard-version DASHBOARD_VERSION
```
`init` exposes many options that can alter any part of the deployment. Within the implementation, argument defaults can be dependent on the presence and value of others (e.g. default `--region` depends on the value of `--provider`).

Example:
```
python automator.py init hub.dirac.institute --provider aws
ls -l hub.dirac.institute
```
```
total 8
drwxr-xr-x  3 steven  staff   96 Dec 19 06:37 cluster
drwxr-xr-x  2 steven  staff   64 Dec 19 06:37 components
-rw-r--r--  1 steven  staff  677 Dec 19 06:37 deploy.yaml
drwxr-xr-x  3 steven  staff   96 Dec 19 06:37 hub
```

# deploy
`deploy` looks at the state of a deployment directory and creates a deployment based on what it finds. It deploys Kubernetes resources and the JupyterHub Helm chart and attempts to make a route between a provided domain name and the external IP of the JupyterHub. 

`deploy` is built to flexibly handle the addition of new Kubernetes resources (e.g. the NVIDIA k8s device plugin, cluster autoscaler, etc.) and the overriding of deployment routines for existing Kubernetes resources.

```
python automator.py deploy --help
```
```
usage: automator.py deploy [-h] deployment

positional arguments:
  deployment

optional arguments:
  -h, --help  show this help message and exit
```

Example
```
python automator.py deploy hub.dirac.institute
```

# edit
`edit` allows the user to edit the state of a deployment directory and is able to handle the addition of custom edit commands and overrides of existing commands.

```
python automator.py edit --help
```
```
usage: automator.py edit [-h] deployment action

positional arguments:
  deployment
  action

optional arguments:
  -h, --help  show this help message and exit
```

Example:
```
python automator.py edit hub.dirac.institute add-nodegroup --size g4dn.xlarge
```
will allow the user to add a nodegroup to their Kubernetes cluster.

# delete
`delete` lets the user tear down the entire cluster + JupyterHub or individual components (theoretically.)

This hasn't been implemented at all other than:
```
python automator.py delete --help
```
```
usage: automator.py delete [-h] [--component COMPONENT] deployment

positional arguments:
  deployment

optional arguments:
  -h, --help            show this help message and exit
  --component COMPONENT
```