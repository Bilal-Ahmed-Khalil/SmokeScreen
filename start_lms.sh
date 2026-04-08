#!/bin/bash
# --- LMS Honeypot Master Boot Script ---

# 1. Ensure MongoDB is running
systemctl start mongod

# 2. Set SigNoz Telemetry Variables (Critical for container networking)
export OTEL_EXPORTER_OTLP_ENDPOINT="http://192.168.23.140:4318"
export OTEL_EXPORTER_OTLP_PROTOCOL="http/protobuf"
export OTEL_RESOURCE_ATTRIBUTES="service.name=lms-honeypot"
export OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true

# 3. Clean up any stale ports from previous crashes
/usr/bin/fuser -k 8000/tcp 8001/tcp

# 4. Navigate to project root and activate venv
cd /root/lms-platform
source venv/bin/activate

# 5. Launch the application in the background
# We use nohup to ensure it keeps running even if the shell closes
nohup python3 backend/run.py >> /root/lms-platform/logs/system_boot.log 2>&1 &
