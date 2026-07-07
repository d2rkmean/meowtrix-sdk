PYTHON = python3
SRC = src/meowtrix/sdk

.PHONY: help format lint check all

format:
	$(PYTHON) -m ruff format $(SRC)

lint:
	$(PYTHON) -m ruff check $(SRC) --fix

mypy:
	$(PYTHON) -m mypy $(SRC)

check: lint mypy

all: format lint mypy