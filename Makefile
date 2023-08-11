.PHONY: install install-dev start flake8 pylint lint

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

start:
	uvicorn main:app --reload

flake8:
	flake8

pylint:
	pylint --fail-under=10 ./*.py

lint: flake8 pylint