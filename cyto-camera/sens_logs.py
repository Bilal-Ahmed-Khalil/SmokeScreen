import json
from opentelemetry import trace
from opentelemetry.trace import get_tracer
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource

# Set up OTLP exporter and tracer
resource = Resource.create({"service.name": "honeypot-logs"})
trace.set_tracer_provider(TracerProvider(resource=resource))
#//////////////////////////////////////////////////
exporter = OTLPSpanExporter(endpoint="http://192.168.23.140:4317", insecure=True)
span_processor = BatchSpanProcessor(exporter)
trace.get_tracer_provider().add_span_processor(span_processor)
tracer = get_tracer(__name__)

# Read JSON logs
with open("/root/bank/logs/activity_log.json", "r") as file:
    logs = json.load(file)

# Send logs as spans
for log in logs:
    with tracer.start_as_current_span(log["action"]) as span:
        span.set_attribute("ip_address", log["ip_address"])
        span.set_attribute("port", log["port"])
        span.set_attribute("timestamp", log["timestamp"])
