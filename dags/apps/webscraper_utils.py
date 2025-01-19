import requests
from bs4 import BeautifulSoup
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


class BeautifulSoupScraper:
    
    def __init__(self, url):
        self.url = url
        self.session = self._create_session()
    
    def request_webpage(self, url: str) -> BeautifulSoup:
        try:
            response = self.session.get(url)
            return BeautifulSoup(response.text, "html.parser")
        except Exception as e:
            raise Exception(f"Failed to request page for {url} after 5 retries with exception:"
                            f" {e}") from e

    def _create_session(self):
        session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=3
        )
        session.mount('https://', HTTPAdapter(max_retries=retries))
        return session
