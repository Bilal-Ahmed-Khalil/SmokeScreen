import json
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# OpenTelemetry setup
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer_provider().get_tracer("honeypot-log")
exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
span_processor = BatchSpanProcessor(exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# File monitoring class
class LogHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith("activity_log.json"):
            print(f"File modified: {event.src_path}")
            try:
                with open(event.src_path, "r") as file:
                    logs = json.load(file)
                    for log in logs:
                        print(f"Sending log: {log}")
                        with tracer.start_as_current_span("honeypot-log") as span:
                            span.set_attribute("action", log["action"])
                            span.set_attribute("ip_address", log["ip_address"])
                            span.set_attribute("port", log["port"])
                            span.set_attribute("timestamp", log["timestamp"])
            except Exception as e:
                print(f"Error reading or sending logs: {e}")

if __name__ == "__main__":
    path = "/home/talha/Desktop/decoys/firealarm/logs/activity_log.json"  # Update with the correct path
    event_handler = LogHandler()
    observer = Observer()
    observer.schedule(event_handler, path=path, recursive=False)
    observer.start()
    print(f"Monitoring {path} for changes...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
