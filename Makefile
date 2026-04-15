PYTHON ?= python3

.PHONY: install run test

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m src.main

test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -s tests -v
