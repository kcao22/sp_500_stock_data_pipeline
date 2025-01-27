import requests
from bs4 import BeautifulSoup
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


class BeautifulSoupScraper:
    
    def __init__(self, url):
        self.url = url
        self.session = self._create_session()

    def _create_session(self):
        session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=3
        )
        session.mount('https://', HTTPAdapter(max_retries=retries))
        return session

    def request_webpage(self, url: str, **kwargs) -> BeautifulSoup:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
            response = self.session.get(
                url=url,
                headers=headers,
                **kwargs
            )
            return BeautifulSoup(response.text, "html.parser")
        except Exception as e:
            raise Exception(f"Failed to request page for {url} after 5 retries with exception:"
                            f" {e}") from e

    def get_element_value(self, soup_object: BeautifulSoup, html_element: str, identifier_attribute:
    str, identifier_attribute_value) -> str:
        try:
            return soup_object.find(html_element, {identifier_attribute:
                                                       identifier_attribute_value}).get("value")
        except Exception as e:
            raise Exception(f"Failed to find HTML element {html_element} with identifier "
                            f"attribute {identifier_attribute} and value "
                            f"{identifier_attribute_value}. \nException: {e}")
