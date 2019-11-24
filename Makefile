all:
	@for cmd in k8s helm dashboard install; do ./scripts/gen-$$cmd; done

destroy:
	@echo "Run ./scripts/gen-destroy"
