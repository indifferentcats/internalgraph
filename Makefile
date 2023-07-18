init:
	. venv/bin/activate && \
	pip install -r requirements.txt

test:
	. venv/bin/activate && \
	python -m unittest discover tests/

build:
	. venv/bin/activate && \
	python -m build

docs:
	. venv/bin/activate; \
	mkdir docs; \
	cd docs; \
	sphinx-quickstart

documentation: docs
	. venv/bin/activate && \
	cd docs && \
	make html

.PHONY: init test build documentation
