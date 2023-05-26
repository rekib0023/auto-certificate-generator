run-localstack:
	docker run --rm -p 4566:4566 localstack/localstack

build-generator:
	docker build --no-cache -t rekib0023/certificate-generator-generator:latest generator/
	docker push rekib0023/certificate-generator-generator:latest

build: build-generator
build: build-stack

deploy-generator-app: 
	kubectl apply -f ./generator/manifests/

deploy-generator-srv:
	docker-compose up --build generator-srv

deploy-gateway-srv:
	docker-compose up --build gateway-srv

deploy-auth-srv:
	docker-compose up --build auth-srv

deploy-event-bus-srv:
	docker-compose up --build event-bus-srv

deploy-workers:
	docker-compose up --build rabbit queue

deploy-localstack:
	docker-compose up --build localstack

deploy-dbs:
	docker-compose up --build generator-db auth-db gateway-db

generator-db-exec:
	docker exec -it generator-db mysql -u root -p

gateway-db-exec:
	docker exec -it -u postgres gateway-db psql

.PHONY: build build-generator deploy-generator-app run-localstack build-stack deploy-generator-srv deploy-gateway-srv deploy-auth-srv deploy-event-bus-srv deploy-workers deploy-localstack deploy-dbs generator-db-exec gateway-db-exec