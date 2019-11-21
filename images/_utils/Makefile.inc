build:
	@echo "$(NAME):$$(hostname)-$$(date '+%Y%m%d%H%M%S')" > .latest.tag.tmp && \
	docker build -t $$(cat .latest.tag.tmp) . && \
	(test -f ../values.yaml && ../_utils/patch-yaml.sh ../values.yaml $(KEY) $$(cat .latest.tag.tmp) && echo "Updated values.yaml with the new image" || true) && \
	mv .latest.tag.tmp latest.tag && \
	echo "Built $$(cat latest.tag); run 'make push' to push it up to the Docker registry"

push:
	@docker push $$(cat latest.tag)
