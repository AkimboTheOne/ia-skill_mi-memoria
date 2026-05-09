.PHONY: test capabilities

test:
	python3 -m unittest discover -s tests

capabilities:
	./bin/mi-memoria capabilities --json
