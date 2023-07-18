.PHONY: stop logs restart bash prune up clean debug build

DOCKER_CORE=core
DOCKER_MONGO=mongo
DOCKER_REDIS=redis
DOCKER_CONTAINERS=$(shell docker ps -a -q)
DOCKER_IMAGES=$(shell docker images -q)

build:
	cp example.env .env
	docker-compose build

stop:
	docker stop $(DOCKER_CORE)
	docker stop $(DOCKER_MONGO)
	docker stop $(DOCKER_REDIS)

logs:
	docker logs $(DOCKER_CORE) -f --tail 50

restart:
	docker restart $(DOCKER_CORE) || true
	docker restart $(DOCKER_MONGO) || true
	docker restart $(DOCKER_REDIS) || true
bash:
	docker exec -it $(DOCKER_CORE) bash
prune:
	docker system prune
up:
	docker-compose up -d

clean:
	docker stop $(DOCKER_CORE)
	docker rm $(DOCKER_CORE)
	docker rmi $(DOCKER_CORE)

clean-all:
	docker stop $(DOCKER_CONTAINERS)   || true
	docker rm $(DOCKER_CONTAINERS)   || true
	docker rmi $(DOCKER_IMAGES)   || true

debug:
	docker attach $(DOCKER_CORE)

seed:
	docker exec $(DOCKER_CORE) pipenv run python3 seed.py seed $(table)

