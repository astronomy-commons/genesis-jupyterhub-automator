all:
	@for cmd in k8s helm dashboard install dns-sync; do ./scripts/gen-$$cmd; done

k8s:
	./scripts/gen-k8s

dns:
	./scripts/gen-dns-sync

helm:
	./scripts/gen-helm

dashboard:
	./scripts/gen-dashboard

install:
	./scripts/gen-install

destroy:
	@echo "Run ./scripts/gen-destroy"
