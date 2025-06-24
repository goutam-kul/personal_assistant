from typing import List, Dict, Optional
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # SECRET_KEY: str ="189447c569350c83639d2f030e0eb21de98785d9bfe749f43bd00c82a4b560c4"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str ="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30



settings = Settings()