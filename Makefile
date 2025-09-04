SHELL := /bin/bash
PY := python3
VENV := .venv
PIP := $(VENV)/bin/pip
PYTHON := $(VENV)/bin/python

.PHONY: help install-deps venv run report exporter enable-systemd clean

help:
	@echo "Targets:"
	@echo "  install-deps   - Install system packages via apt (Ubuntu/Kali)"
	@echo "  venv           - Create Python venv and install requirements"
	@echo "  run            - Run SecureWatch one-off scan"
	@echo "  report         - Regenerate HTML report from latest JSON"
	@echo "  exporter       - Run Prometheus exporter on :9109"
	@echo "  enable-systemd - Install and enable systemd timer (hourly)"
	@echo "  clean          - Remove venv and generated artifacts"

install-deps:
	sudo bash scripts/install.sh

venv:
	test -d $(VENV) || $(PY) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r python/requirements.txt

run:
	bash scripts/securewatch.sh

report:
	$(PYTHON) python/report_generator.py

exporter:
	$(PYTHON) python/exporters/securewatch_exporter.py

enable-systemd:
	@echo "Installing systemd units..."
	@sudo cp systemd/securewatch.service /etc/systemd/system/securewatch.service
	@sudo cp systemd/securewatch.timer /etc/systemd/system/securewatch.timer
	@sudo systemctl daemon-reload
	@sudo systemctl enable --now securewatch.timer
	@echo "Exporter service is optional; edit path then enable if desired:"
	@echo "  sudo cp systemd/securewatch-exporter.service /etc/systemd/system/"
	@echo "  sudo systemctl daemon-reload && sudo systemctl enable --now securewatch-exporter.service"

clean:
	rm -rf $(VENV) data/reports/*.html data/logs/*.json data/logs/*.ndjson || true
