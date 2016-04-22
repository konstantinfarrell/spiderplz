.PHONY: run install clean

VENV_DIR ?= .env
PYTHON = python3

run:
	clear
	$(PYTHON) crawl.py

init:
	rm -rf $(VENV_DIR)
	@$(MAKE) $(VENV_DIR)

clean:
	find . -iname "*.pyc" -delete
	find . -iname "*.pyo" -delete
	find . -iname "__pycache__" -delete

$(VENV_DIR):
	virtualenv --no-site-packages -p $(PYTHON) $(VENV_DIR)
	$(VENV_DIR)/bin/pip install -r requirements.txt
