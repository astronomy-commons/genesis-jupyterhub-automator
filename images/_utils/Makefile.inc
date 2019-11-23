#
# NAME and KEY must be defined by the including makefile
#

# Check if bin/ is on the path
ifneq (, $(shell hash sht-expand 2>&1))
  $(error "No sht-expand in $$PATH. Is genesis-jupyterhub-automator's bin/ on it?")
endif

TAG:=$(shell hostname)-$(shell date '+%Y%m%d%H%M%S')

build:
	@echo "$(NAME):$(TAG)" > .latest.tag.tmp && \
	docker build -t $$(cat .latest.tag.tmp) . && \
	sht-expand $(KEY).yaml.sht NAME=$(NAME) TAG=$(TAG) > $(KEY).yaml && \
	mv .latest.tag.tmp latest.tag && \
	echo "Built $$(cat latest.tag); run 'make push' to push it up to the Docker registry"

push:
	@docker push $$(cat latest.tag)

##	(test -f ../values.yaml && ../_utils/patch-yaml-autoexec.sh ../values.yaml autoexec.sh && echo "Updated values.yaml autoexec.sh commands" || true) && 
