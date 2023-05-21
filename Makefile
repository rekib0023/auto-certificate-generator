run-localstack:
	docker run --rm -p 4566:4566 localstack/localstack

build-generator:
	docker build --no-cache -t rekib0023/certificate-generator-generator:latest generator/
	docker push rekib0023/certificate-generator-generator:latest

build: build-generator
build: build-stack

deploy-generator-app: 
	kubectl apply -f ./generator/manifests/

.PHONY: build build-generator deploy-generator-app run-localstack build-stack