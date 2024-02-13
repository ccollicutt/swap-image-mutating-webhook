# Set the REGISTRY with the ?= operator, so that it can be overridden by an environment variable
REGISTRY ?= someregistry
IMAGE_NAME ?= blockfriday:latest

.PHONY: all image push rollout

all: test image push rollout

image:
	@echo "Building docker image ${REGISTRY}/${IMAGE_NAME}..."
	@docker build -t ${REGISTRY}/$(IMAGE_NAME) .

push:
	@echo "Pushing docker image ${REGISTRY}/${IMAGE_NAME}..."
	@docker push ${REGISTRY}/${IMAGE_NAME}

deploy:
	#kubectl create -f manifests/namespace.yaml
	#sleep 3
	kubectl create -f manifests/certs.yaml
	kubectl create -f manifests/mutating-webhook-configuration.yaml
	kubectl create -f manifests/deployment.yaml
	kubectl create -f manifests/service.yaml

update:
	kubectl create -f manifests/namespace.yaml || true
	sleep 3
	kubectl create -f manifests/certs.yaml || true
	kubectl create -f manifests/mutating-webhook-configuration.yaml || true
	kubectl create -f manifests/deployment.yaml || true
	kubectl create -f manifests/service.yaml || true

delete:
	#kubectl delete -f manifests/namespace.yaml || true
	kubectl delete -f manifests/certs.yaml || true
	kubectl delete -f manifests/mutating-webhook-configuration.yaml || true
	kubectl delete -f manifests/deployment.yaml || true
	kubectl delete -f manifests/service.yaml || true

rollout:
	kubectl -n swap-image rollout restart deployment/swap-image 

deploy-test:
	kubectl create -f manifests/test-namespace.yaml || true
	kubectl create -f manifests/test-deployment.yaml || true

redo-test:
	kubectl delete -f manifests/test-deployment.yaml || true
	kubectl create -f manifests/test-deployment.yaml || true

test:
	cd app && python -m unittest discover tests -v

git:
	git add .
	git commit -m "update"
	git push

compare-lines:
	@echo "Counting lines in Python files..."
	@find ./app -name '*.py' | xargs wc -l
	@echo "Counting lines in YAML files..."
	@find . -name '*.yaml' -o -name '*.yml' | xargs wc -l
