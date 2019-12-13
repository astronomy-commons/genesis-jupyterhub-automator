.PHONY: all
all:
	@for cmd in k8s helm dashboard install dns-sync; do ./scripts/gen-$$cmd; done

.PHONY: k8s
k8s:
	./scripts/gen-k8s

.PHONY: dns
dns:
	./scripts/gen-dns-sync

.PHONY: helm
helm:
	./scripts/gen-helm

.PHONY: dashboard
dashboard:
	./scripts/gen-dashboard

.PHONY: install
install:
	./scripts/gen-install

.PHONY: destroy
destroy:
	@echo "Run ./scripts/gen-destroy"
