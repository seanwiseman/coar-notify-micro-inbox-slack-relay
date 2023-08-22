.PHONY: install install-dev start flake8 pylint lint venv-create

VENV = venv
PIP = $(VENV)/bin/pip
PYTHON = $(VENV)/bin/python


venv-create:
	python3 -m venv $(VENV)

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.dev.txt

start:
	uvicorn main:app --reload

flake8:
	flake8

pylint:
	pylint --fail-under=10 ./*.py

lint: flake8 pylint