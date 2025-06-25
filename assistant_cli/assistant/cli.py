import click
import requests
from datetime import datetime
from assistant.api_client import APIClient
from assistant.config import save_token
from assistant.daemon import start_daemon, stop_daemon
from loguru import logger

@click.group()
def cli():
    pass

@cli.command()
@click.argument("user_id")
@click.argument("password")
def login(user_id, password):
    # logger.debug("Log in called")
    client = APIClient()
    if client.login(user_id, password):
        if client.token is not None:
            # logger.debug("Token found. Saving token!")
            save_token(client.token)
            click.echo("Login successful!")
    else:
        click.echo("Login failed.")

@cli.group()
def task():
    pass

@task.command()
@click.argument("title")
@click.argument("priority", type=int)
@click.option("--description")
@click.option("--due-date")
def add_task(title, priority, description, due_date):
    client = APIClient()
    if not client.token:
        click.echo("Please login first.")
        return
    data = {"title": title, "priority": priority}
    if description:
        data["description"] = description
    if due_date:
        data["due_date"] = due_date
    try:
        response = client.post("tasks", data)
        click.echo(f"Task created: {response['title']} (ID: {response['task_id']})")
    except requests.RequestException as e:
        click.echo(f"Error: {e}")

@task.command()
def list_task():
    client = APIClient()
    if not client.token:
        click.echo("Please login first.")
        return
    try:
        tasks = client.get("tasks")
        for task in tasks:
            click.echo(f"ID: {task['task_id']} | {task['title']} | Priority: {task['priority']} | Status: {task['status']}")
    except requests.RequestException as e:
        click.echo(f"Error: {e}")

@task.command()
@click.argument("task_id", type=int)
@click.option("--title")
@click.option("--priority", type=int)
@click.option("--status")
def update(task_id, title, priority, status): #TODO: allow due_date & description
    client = APIClient()
    if not client.token:
        click.echo("Please login first.")
        return
    data = {}
    if title:
        data["title"] = title
    if priority:
        data["priority"] = priority
    if status:
        data["status"] = status
    try:
        response = client.patch(f"tasks/{task_id}", data)
        click.echo(f"Task updated: {response['title']}")
    except requests.RequestException as e:
        click.echo(f"Error: {e}")

@task.command()
@click.argument("task_id", type=int)
def delete(task_id):
    client = APIClient()
    if not client.token:
        click.echo("Please login first.")
        return
    try:
        client.delete(f"tasks/{task_id}")
        click.echo(f"Task {task_id} deleted.")
    except requests.RequestException as e:
        click.echo(f"Error: {e}")

@cli.group()
def reminder():
    pass

@reminder.command()
@click.argument("task_id", type=int)
@click.argument("reminder_time")
@click.argument("method")
def add_reminder(task_id, reminder_time, method):
    client = APIClient()
    if not client.token:
        click.echo("Please login first.")
        return
    data = {"task_id": task_id, "reminder_time": reminder_time, "method": method}
    try:
        response = client.post("reminders", data)
        click.echo(f"Reminder created: Task {response['task_id']} (ID: {response['reminder_id']})")
    except requests.RequestException as e:
        click.echo(f"Error: {e}")

@reminder.command()
def _task():
    client = APIClient()
    if not client.token:
        click.echo("Please login first.")
        return
    try:
        reminders = client.get("reminders")
        for reminder in reminders:
            click.echo(f"ID: {reminder['reminder_id']} | Task: {reminder['task_id']} | Time: {reminder['reminder_time']} | Method: {reminder['method']}")
    except requests.RequestException as e:
        click.echo(f"Error: {e}")

@cli.group()
def daemon():
    pass

@daemon.command()
def start():
    start_daemon()
    click.echo("Daemon started.")

@daemon.command()
def stop():
    stop_daemon()
    click.echo("Daemon stopped.")