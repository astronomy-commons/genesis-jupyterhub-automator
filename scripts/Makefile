all:
	@for cmd in k8s helm dashboard install dns-sync; do ./scripts/gen-$$cmd; done

destroy:
	@echo "Run ./scripts/gen-destroy"
