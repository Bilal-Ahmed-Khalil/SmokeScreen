import json
import os
from opentelemetry import trace
from opentelemetry.trace import get_tracer
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource

# --- STEP 1: OPEN-TELEMETRY CONFIGURATION ---

# Define the service name as it will appear in your dashboard (e.g., Jaeger/SigNoz)
resource = Resource.create({"service.name": "SmokeScreen-Honeypot-Telemetry"})
trace.set_tracer_provider(TracerProvider(resource=resource))

# Configure the OTLP Exporter to point to your OpenTelemetry Collector
# Endpoint: The IP of your management server running the OTLP listener
exporter = OTLPSpanExporter(endpoint="http://192.168.23.140:4317", insecure=True)

# Use BatchSpanProcessor for better performance (groups spans before sending)
span_processor = BatchSpanProcessor(exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Initialize the tracer object
tracer = get_tracer(__name__)

# --- STEP 2: LOG PROCESSING ---

LOG_PATH = "/root/cyto-camera/logs/flask-logs.json"

def push_logs_to_telemetry():
    """Reads local JSON logs and exports them as distributed traces."""
    
    if not os.path.exists(LOG_PATH):
        print(f"[!] Error: Log file not found at {LOG_PATH}")
        return

    try:
        with open(LOG_PATH, "r") as file:
            logs = json.load(file)
            
        print(f"[*] Found {len(logs)} log entries. Exporting to collector...")

        # Iterate through each log entry and convert it into a Trace Span
        for log in logs:
            # The action (e.g., 'login failed') becomes the Span name
            with tracer.start_as_current_span(log["action"]) as span:
                # Attach metadata as attributes for filtering in the dashboard
                span.set_attribute("attacker.ip", log["ip_address"])
                span.set_attribute("attacker.port", log["port"])
                span.set_attribute("event.timestamp", log["timestamp"])
                
        print("[+] Telemetry export complete.")

    except json.JSONDecodeError:
        print("[!] Error: Could not parse JSON. The log file might be empty or corrupted.")
    except Exception as e:
        print(f"[!] An unexpected error occurred: {e}")

# --- EXECUTION ---

if __name__ == "__main__":
    push_logs_to_telemetry()
