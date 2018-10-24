.PHONY: clean
clean:
	rm -rf redisclustermon.egg-info
	rm -f dist/*.gz

.PHONY: pyrcm
pyrcm:
	python setup.py sdist
	rm -rf redisclustermon.egg-info

.PHONY: client
client:
	cd client; npm install; ng build;

.PHONY: docker
docker: pyrcm client
	docker build -t rcm .
