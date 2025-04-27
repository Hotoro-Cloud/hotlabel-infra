import json
import time
from typing import Any, Dict, Optional

import requests
from tenacity import retry, stop_after_attempt, wait_fixed

from config import DEFAULT_HEADERS, RETRY_ATTEMPTS, RETRY_DELAY


class APIClient:
    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url
        self.headers = headers or DEFAULT_HEADERS.copy()

    @retry(stop=stop_after_attempt(RETRY_ATTEMPTS), wait=wait_fixed(RETRY_DELAY))
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}{endpoint}",
            headers=self.headers,
            params=params,
        )
        response.raise_for_status()
        return response.json()

    @retry(stop=stop_after_attempt(RETRY_ATTEMPTS), wait=wait_fixed(RETRY_DELAY))
    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}{endpoint}",
            headers=self.headers,
            json=data,
        )
        response.raise_for_status()
        return response.json()

    @retry(stop=stop_after_attempt(RETRY_ATTEMPTS), wait=wait_fixed(RETRY_DELAY))
    def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.put(
            f"{self.base_url}{endpoint}",
            headers=self.headers,
            json=data,
        )
        response.raise_for_status()
        return response.json()

    @retry(stop=stop_after_attempt(RETRY_ATTEMPTS), wait=wait_fixed(RETRY_DELAY))
    def delete(self, endpoint: str) -> Dict[str, Any]:
        response = requests.delete(
            f"{self.base_url}{endpoint}",
            headers=self.headers,
        )
        response.raise_for_status()
        return response.json()


def wait_for_service(url: str, timeout: int = 30) -> bool:
    """Wait for a service to become available."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(1)
    return False


def cleanup_test_data(client: APIClient, endpoint: str, test_id: str) -> None:
    """Clean up test data after tests."""
    try:
        client.delete(f"{endpoint}/{test_id}")
    except requests.RequestException:
        pass  # Ignore cleanup errors 