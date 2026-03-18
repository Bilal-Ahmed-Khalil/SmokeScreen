import time
import os
import re
from opentelemetry import _logs
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry._logs import SeverityNumber

# 1. SETUP
SIGNOZ_ENDPOINT = "http://127.0.0.1:4317" 
WATCH_CONFIG = {
    "lms_web": {
        "path": "/home/kali/Desktop/FYP/lms-platform/backend/access.log",
    },
    "snort_ids": {
        "path": "/var/log/snort/alert_fast.txt",
    }
}

# Initialize OTel Logging
resource = Resource.create({"service.name": "LMS-Security-Center"})
logger_provider = LoggerProvider(resource=resource)
exporter = OTLPLogExporter(endpoint=SIGNOZ_ENDPOINT, insecure=True)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
_logs.set_logger_provider(logger_provider)
logger = _logs.get_logger(__name__)

def parse_line(line, source):
    """Parses logs and forces current timestamp for SigNoz"""
    if not line.strip(): return
    
    attr = {
        "log.source": source,
        "event.timestamp": time.strftime('%Y-%m-%d %H:%M:%S') # Force current time
    }
    
    if source == "lms_web":
        ip_match = re.search(r'IP: (\d+\.\d+\.\d+\.\d+)', line)
        user_match = re.search(r'user: (\S+)', line)
        if ip_match: attr["attacker.ip"] = ip_match.group(1)
        if user_match: attr["target.user"] = user_match.group(1)
        severity = SeverityNumber.INFO
        
    elif source == "snort_ids":
        # Improved Snort 3 parser to ignore the old 02/05 timestamps in the string
        snort_ip_match = re.search(r'\} (\d+\.\d+\.\d+\.\d+)', line)
        if snort_ip_match: attr["attacker.ip"] = snort_ip_match.group(1)
        attr["attack.type"] = "Network_Scan"
        severity = SeverityNumber.WARN 

    print(f"📡 [{source}] Shipping New Log: {line.strip()}")
    logger.emit(
        body=line.strip(), 
        severity_number=severity, 
        attributes=attr
    )

def ship_logs():
    print(f"🚀 SigNoz Multi-Shipper Active! (Tailing New Logs Only)")
    
    files = {}
    for name, config in WATCH_CONFIG.items():
        path = config['path']
        if not os.path.exists(path):
            print(f"⚠️ Warning: {path} not found.")
            continue
            
        f = open(path, "r")
        f.seek(0, os.SEEK_END) # Start at end of file to ignore history
        files[name] = {"handle": f, "path": path, "size": os.path.getsize(path)}
        print(f"📂 Watching {name}: {path}")

    try:
        while True:
            for name, info in files.items():
                # Check if file was cleared/truncated (size decreased)
                current_size = os.path.getsize(info['path'])
                if current_size < info['size']:
                    print(f"♻️ Log cleared for {name}, resetting pointer...")
                    info['handle'].seek(0)
                
                line = info['handle'].readline()
                if line:
                    parse_line(line, name)
                
                info['size'] = current_size
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n👋 Stopping Multi-Shipper...")
    finally:
        for info in files.values():
            info['handle'].close()

if __name__ == "__main__":
    ship_logs()
