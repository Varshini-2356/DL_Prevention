import time
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from difflib import SequenceMatcher
import socket

TWILIO_SID=ACxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH=xxxxxxxxxxxxxxxxxxxxxx
TWILIO_FROM=+1xxxxxxxxx
TWILIO_TO=+91xxxxxxxxx


files_to_monitor = [
   "1st file's path",
   "2nd file's path also include more"
]

previous_contents = {}

def track_changes(old_content, new_content):
    """Detect changes between old and new content."""
    changes = []
    matcher = SequenceMatcher(None, old_content.split(), new_content.split())
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'replace':
            changes.append(f"Replaced '{' '.join(old_content.split()[i1:i2])}' with '{' '.join(new_content.split()[j1:j2])}'")
        elif tag == 'delete':
            changes.append(f"Deleted '{' '.join(old_content.split()[i1:i2])}'")
        elif tag == 'insert':
            changes.append(f"Inserted '{' '.join(new_content.split()[j1:j2])}'")
    return changes

def send_sms_notification(file_path, changes, retry_attempts=3):
    """Send SMS with changes detected in the file."""
    for attempt in range(retry_attempts):
        try:
            client = Client(ACCOUNT_SID, AUTH_TOKEN)
            change_details = "\n".join(changes)
            message_body = f"Alert: The file {file_path} has been modified.\nChanges:\n{change_details}"
            
            message = client.messages.create(
                from_=FROM_PHONE,
                body=message_body,
                to=TO_PHONE
            )
            print(f"SMS sent for file change: {file_path} with SID: {message.sid}")
            return  
        except TwilioRestException as e:
            print(f"Twilio error on attempt {attempt + 1}: {e}")
        except socket.gaierror as e:
            print(f"Network error on attempt {attempt + 1}: {e}")
        except Exception as e:
            print(f"Error sending SMS on attempt {attempt + 1}: {e}")
        time.sleep(2)  
    print(f"Failed to send SMS after {retry_attempts} attempts.")

class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        """Handle file modification event."""
        global previous_contents
        normalized_path = os.path.normpath(event.src_path)
        for file_path in files_to_monitor:
            if os.path.normpath(file_path) == normalized_path:
                print(f"File {file_path} has been modified.")
                try:
                    with open(file_path, 'r') as file:
                        new_content = file.read()
                    if file_path in previous_contents:
                        old_content = previous_contents[file_path]
                        changes = track_changes(old_content, new_content)
                        if changes:
                            send_sms_notification(file_path, changes)
                    else:
                        print(f"Initial content loaded for {file_path}. No changes to compare yet.")
                    previous_contents[file_path] = new_content
                except Exception as e:
                    print(f"Error reading file: {e}")

def monitor_files(file_paths):
    """Monitor multiple files for changes."""
    global previous_contents
    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"Error: The file {file_path} does not exist.")
            continue

        try:
            with open(file_path, 'r') as file:
                previous_contents[file_path] = file.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
    event_handler = FileChangeHandler()
    observer = Observer()
    monitored_dirs = set()
    for file_path in file_paths:
        directory = os.path.dirname(file_path)
        if directory not in monitored_dirs:
            observer.schedule(event_handler, directory, recursive=False)
            monitored_dirs.add(directory)

    print(f"Monitoring started on the following files:\n{', '.join(file_paths)}")
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("Monitoring stopped.")
    observer.join()

if __name__ == "__main__":

    monitor_files(files_to_monitor)
