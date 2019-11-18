all: jhub
	@echo Done.

k8s:
	@doctl k8s cluster list --format Name --no-header | grep -qE '^genesis$$' && \
	  echo "cluster $(CLUSTER_NAME) already exists. skipping creation." || ( \
	  echo "=========== Creating k8s cluster..." && \
	  doctl k8s cluster create $(CLUSTER_NAME) --region $(REGION) --node-pool="name=$(NODE_POOL_NAME);size=$(SIZE);count=$(NODES)" --version="$(K8S_VERSION)" \
	  )
	@ [[ $$(kubectl config current-context) != "$(CONTEXT)" ]] && kubectl config use-context $(CONTEXT) || true

helm: k8s
	@kubectl get serviceAccounts --namespace kube-system  | grep -qE '^tiller .*$$' && \
	  echo "helm already installed. skipping installation." \
	  || ( \
	      echo "=========== Installing Helm..." && \
	      kubectl --namespace kube-system create serviceaccount tiller && \
	      kubectl create clusterrolebinding tiller --clusterrole cluster-admin --serviceaccount=kube-system:tiller && \
	      helm init --service-account tiller --wait && \
	      kubectl patch deployment tiller-deploy --namespace=kube-system --type=json \
	        --patch='[{"op": "add", "path": "/spec/template/spec/containers/0/command", "value": ["/tiller", "--listen=localhost:44134"]}]' \
	  )

dashboard: helm
	@ # Set up k8s web dashboard (check for new versions at https://github.com/kubernetes/dashboard/releases)
	@[[ -z "$$(kubectl get pods -n kubernetes-dashboard 2>/dev/null)" ]] && ( \
	  echo "=========== Installing Kubernetes Dashboard..." && \
	  (kubectl delete ns kubernetes-dashboard 2>/dev/null || true) && \
	  kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.0.0-beta6/aio/deploy/recommended.yaml && \
	  \
	  kubectl apply -f deploy/create-dashboard-admin-user.yaml && \
	  mkdir -p etc/secrets && \
	  \
	  kubectl -n kubernetes-dashboard describe secret \
	    $$(kubectl -n kubernetes-dashboard get secret | grep admin-user | awk '{print $$1}') \
	    | grep -E '^token:' | sed 's/^token: *//' > etc/secrets/dashboard.token && \
	  \
	  echo "" && \
	  echo "Dashboard installed; the password token is in 'etc/secrets/dashboard.token'" && \
	  echo "Run 'kubectl proxy &', and visit http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/#/login" \
	) || echo "dashboard already installed. skipping installation"

jhub: dashboard
	@[[ -z "$$(kubectl get pods -n $(JHUB_K8S_NAMESPACE) 2>/dev/null)" ]] && ( \
	  echo "=========== Installing JupyterHub ============ ..." && \
	  helm repo add jupyterhub https://jupyterhub.github.io/helm-chart/ && \
	  helm repo update && \
	  \
	  ./bin/deploy.sh \
	) || echo "JupyterHub already deployed. skipping deployment."

	@./bin/add-to-dns.sh

.PHONY: deploy
deploy:
	@ ./bin/deploy.sh
	@ ./bin/add-to-dns.sh

destroy:
	@echo "=========== Destroying everything ============ ..."
	helm delete "$(JHUB_HELM_RELEASE)" --purge
	kubectl delete namespace "$(JHUB_K8S_NAMESPACE)"
	doctl k8s cluster delete "$(CLUSTER_NAME)" -f

include etc/Makefile.config
