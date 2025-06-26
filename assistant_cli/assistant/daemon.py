import requests
import notify2
from apscheduler.schedulers.blocking import BlockingScheduler
from assistant.api_client import APIClient
from assistant.config import load_token
from datetime import datetime, timezone
import os
import signal
import sys
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.expanduser('~/.assistant_daemon.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

scheduler = BlockingScheduler()
PID_FILE = os.path.expanduser("~/.assistant_daemon.pid")

def send_notification(title: str, message: str):
    try:
        notify2.init("Assistant")
        n = notify2.Notification(title, message)
        n.show()
        logger.info(f"Notification sent: {title}")
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")

def check_reminders():
    logger.info("Checking reminders...")
    client = APIClient()
    if not client.token:
        logger.warning("No token available")
        return
    
    try:
        reminders = client.get("reminders")
        logger.info(f"Found {len(reminders)} reminders")
        
        for reminder in reminders:
            reminder_time = datetime.fromisoformat(reminder["reminder_time"].replace("Z", "+00:00"))
            if reminder_time <= datetime.now(timezone.utc):
                send_notification(
                    f"Reminder: Task {reminder['task_id']}",
                    f"Method: {reminder['method']}"
                )
                client.delete(f"reminders/{reminder['reminder_id']}")
                logger.info(f"Processed reminder {reminder['reminder_id']}")
    except requests.RequestException as e:
        logger.error(f"API request failed: {e}")
    except Exception as e:
        logger.error(f"Error checking reminders: {e}")

def signal_handler(signum, frame):
    logger.info("Received signal to stop daemon")
    cleanup_and_exit()

def cleanup_and_exit():
    logger.info("Shutting down daemon...")
    if scheduler.running:
        scheduler.shutdown()
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)
    sys.exit(0)

def start_daemon():
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, "r") as f:
                pid = int(f.read().strip())
            # Check if process is actually running
            os.kill(pid, 0)
            print("Daemon already running.")
            return
        except (OSError, ValueError):
            # PID file exists but process is not running
            os.remove(PID_FILE)
    
    # Write PID file
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))
    
    # Set up signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    logger.info("Starting daemon...")
    
    # Add job to scheduler
    scheduler.add_job(check_reminders, "interval", minutes=1)
    
    try:
        # This will block and keep the daemon running
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Daemon interrupted")
    finally:
        cleanup_and_exit()

def stop_daemon():
    if not os.path.exists(PID_FILE):
        print("Daemon not running.")
        return
    
    try:
        with open(PID_FILE, "r") as f:
            pid = int(f.read().strip())
        
        logger.info(f"Stopping daemon with PID {pid}")
        os.kill(pid, signal.SIGTERM)
        
        # Wait for process to stop
        time.sleep(2)
        
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        
        print("Daemon stopped.")
    except (OSError, ValueError) as e:
        logger.error(f"Error stopping daemon: {e}")
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)

def is_daemon_running():
    if not os.path.exists(PID_FILE):
        return False
    
    try:
        with open(PID_FILE, "r") as f:
            pid = int(f.read().strip())
        # Check if process is actually running
        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        # PID file exists but process is not running
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        return False