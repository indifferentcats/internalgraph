init:
	. venv/bin/activate && \
	pip install -r requirements.txt

test:
	. venv/bin/activate && \
	python -m unittest discover tests/

build:
	. venv/bin/activate && \
	python -m build

.PHONY: init test build
