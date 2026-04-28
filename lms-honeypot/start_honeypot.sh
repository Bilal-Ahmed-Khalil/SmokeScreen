#!/bin/bash
export OTEL_EXPORTER_OTLP_ENDPOINT="http://192.168.23.140:4318"
export OTEL_EXPORTER_OTLP_PROTOCOL="http/protobuf"
export OTEL_RESOURCE_ATTRIBUTES="service.name=lms-honeypot"
# NEW: This sends ALL python logging module logs to SigNoz
export OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true

source venv/bin/activate
opentelemetry-instrument \
    --traces_exporter otlp \
    --metrics_exporter otlp \
    --logs_exporter otlp \
    python3 backend/run.py
