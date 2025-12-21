import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Define the handler for file modification
class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith("activity_log.json"):
            print(f"File modified: {event.src_path}")
            os.system("python3 send_logs_1.py")  # Executes the send_logs_1.py script

if __name__ == "__main__":
    path = "/home/talha/Desktop/decoys/firealarm/logs/activity_log.json"  # Update to the correct file path
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(path), recursive=False)
    observer.start()
    print(f"Monitoring {path} for changes...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
