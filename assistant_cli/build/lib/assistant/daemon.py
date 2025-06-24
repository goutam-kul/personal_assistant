import requests
import notify2
from apscheduler.schedulers.background import BackgroundScheduler
from .api_client import APIClient
from .config import load_token
from datetime import datetime
import os

scheduler = BackgroundScheduler()
PID_FILE = os.path.expanduser("~/.assistant_daemon.pid")

def send_notification(title: str, message: str):
    notify2.init("Assistant")
    n = notify2.Notification(title, message)
    n.show()

def check_reminders():
    client = APIClient()
    if not client.token:
        return
    try:
        reminders = client.get("reminders")
        for reminder in reminders:
            reminder_time = datetime.fromisoformat(reminder["reminder_time"].replace("Z", "+00:00"))
            if reminder_time <= datetime.utcnow():
                send_notification(
                    f"Reminder: Task {reminder['task_id']}",
                    f"Method: {reminder['method']}"
                )
                client.delete(f"reminders/{reminder['reminder_id']}")
    except requests.RequestException:
        pass

def start_daemon():
    if os.path.exists(PID_FILE):
        print("Daemon already running.")
        return
    scheduler.add_job(check_reminders, "interval", minutes=1)
    scheduler.start()
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

def stop_daemon():
    if not os.path.exists(PID_FILE):
        print("Daemon not running.")
        return
    with open(PID_FILE, "r") as f:
        pid = int(f.read())
    os.kill(pid, 15)  # SIGTERM
    os.remove(PID_FILE)
    scheduler.shutdown()