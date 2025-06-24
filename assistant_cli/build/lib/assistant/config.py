from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:5000")
TOKEN_FILE = os.path.expanduser("~/.assistant_token")

def save_token(token: str):
    with open(TOKEN_FILE, "w") as f:
        f.write(token)


def load_token() -> Optional[str]:
    try:
        with open(TOKEN_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None
    
