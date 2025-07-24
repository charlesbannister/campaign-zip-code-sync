import requests
import time

class ZipCodeFetcher:
    def __init__(self, url: str, max_retries: int = 5, backoff_factor: float = 1.0):
        self.url = url
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    def fetch(self):
        attempt = 0
        while attempt < self.max_retries:
            try:
                response = requests.get(self.url, timeout=10)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                attempt += 1
                if attempt == self.max_retries:
                    raise
                sleep_time = self.backoff_factor * (2 ** (attempt - 1))
                print(f"Fetch failed (attempt {attempt}/{self.max_retries}): {e}. Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
