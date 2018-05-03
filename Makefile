CONTAINER_NAME=dumpy
REGISTRY=$(CONTAINER_NAME)
.PHONY: all build push

all: build push clean

build:
ifndef VERSION
	$(error VERSION is undefined - run using make docker-build VERSION=vX.Y.Z)
endif
	find ./dumpy -iname '*.pyc' -delete
	docker build -t $(REGISTRY):$(VERSION) .

push:
ifndef VERSION
	$(error VERSION is undefined - run using make docker-push VERSION=vX.Y.Z)
endif
	docker push $(REGISTRY):$(VERSION)

clean:
ifndef VERSION
	$(error VERSION is undefined - run using make clean VERSION=vX.Y.Z)
endif
	docker rmi -f $(REGISTRY):$(VERSION)