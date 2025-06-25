from typing import Dict
import requests
from assistant.config import API_URL, load_token
from loguru import logger

class APIClient:
    def __init__(self) -> None:
        self.base_url = API_URL
        self.token = load_token()

    def _headers(self):
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
    
    def login(self, user_id: str, password: str) -> bool:
        try:
            # logger.debug("Response generating")
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={"user_id": user_id, "password": password}
            )
            # logger.debug("response generated")
            # logger.debug(f"Raw response: {response.json()}")

            response.raise_for_status()
            self.token = response.json()["access_token"]

            # logger.debug(f"Token: {self.token}") 
            return True
        except requests.RequestException:
            return False
        
    def post(self, endpoint: str, data: Dict) -> Dict:
        response = requests.post(
            f"{self.base_url}/{endpoint}", 
            json=data,
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get(self, endpoint: str) -> Dict:
        response = requests.get(
            f"{self.base_url}/{endpoint}",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()
    
    def patch(self, endpoint: str, data: Dict) -> Dict:
        response = requests.patch(
            f"{self.base_url}/{endpoint}", 
            json=data,
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()
    
    def delete(self, endpoint: str):
        response = requests.delete(
            f"{self.base_url}/{endpoint}",
            headers=self._headers()
        )
        response.raise_for_status()