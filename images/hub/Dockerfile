FROM jupyterhub/k8s-hub:0.9.0-alpha.1.020.c70f016

USER root

# Patch https://github.com/jupyterhub/kubespawner/issues/354
COPY spawner.py /usr/local/lib/python3.6/dist-packages/kubespawner/spawner.py

# Customize the logo
COPY dirac-jupyter-logo.png /usr/local/share/jupyter/hub/static/images/logo.png

USER ${NB_USER}
