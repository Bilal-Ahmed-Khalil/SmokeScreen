import json
import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.trace import OTLPSpanExporter  # Updated import

# Initialize the OpenTelemetry Tracer
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Set up OTLP exporter and processor
exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
span_processor = BatchSpanProcessor(exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Path to the activity log file
LOG_FILE_PATH = 'activity_log.json'

class LogHandler(FileSystemEventHandler):
    def __init__(self, tracer):
        self.tracer = tracer

    def on_modified(self, event):
        if event.src_path == LOG_FILE_PATH:
            print(f'File {LOG_FILE_PATH} has been modified, sending new logs...')
            self.send_logs()

    def send_logs(self):
        # Read the new log entries from the file
        try:
            with open(LOG_FILE_PATH, 'r') as file:
                logs = json.load(file)
                for log_entry in logs:
                    self.send_log_to_otlp(log_entry)
        except Exception as e:
            print(f"Error reading log file: {e}")

    def send_log_to_otlp(self, log_entry):
        action = log_entry.get("action")
        ip_address = log_entry.get("ip_address")
        port = log_entry.get("port")
        timestamp = log_entry.get("timestamp")
        
        # Start a span to represent this log entry
        with self.tracer.start_as_current_span("honeypot-log"):
            span = trace.get_current_span()
            span.set_attribute("action", action)
            span.set_attribute("ip_address", ip_address)
            span.set_attribute("port", port)
            span.set_attribute("timestamp", timestamp)
            print(f"Log sent to OTLP: {action} from {ip_address}:{port} at {timestamp}")

# Set up the file system observer to monitor log file changes
if __name__ == '__main__':
    event_handler = LogHandler(tracer)
    observer = Observer()
    observer.schedule(event_handler, path='./', recursive=False)  # monitor current directory
    observer.start()
    
    print(f"Monitoring {LOG_FILE_PATH} for changes...")

    try:
        while True:
            time.sleep(1)  # Keep the script running
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
