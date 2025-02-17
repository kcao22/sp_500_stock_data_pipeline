import requests
from bs4 import BeautifulSoup
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


class BeautifulSoupScraper:

    def __init__(self):
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
            raise Exception(f"Failed to request page for {url} after 5 retries with exception:\n{e}") from e

    def get_element_data_value(
            self,
            soup_object: BeautifulSoup,
            html_element_tag: str,
            identifier_attribute: str,
            identifier_value: str
    ) -> str:
        try:
            element = soup_object.find(html_element_tag, {identifier_attribute: identifier_value})
            if not element:
                return None
            if element.has_attr("data-value"):
                return element["data-value"].strip()
            else:
                return element.text.strip()
        except Exception as e:
            raise Exception(f"Get element failed for {html_element_tag}, identifier attribute {identifier_attribute}, and identifier_value {identifier_value} with exception: {e}")

    def get_element_text_value(
            self,
            soup_object: BeautifulSoup,
            html_element_tag: str,
            text_class_name: str,
            text_class_filter: str,
            sibling_html_element_value_tag: str = None,
            sibling_html_element_value_class: str = None,
            is_nested: bool = False
    ) -> str:
        try:
            label_span = soup_object.find(name=html_element_tag, class_=text_class_name, string=lambda text: text and text.strip() == text_class_filter.strip())
            if not label_span:
                return None
            else:
                if is_nested:
                    value_span = label_span.find_next_sibling(name=sibling_html_element_value_tag, class_=sibling_html_element_value_class)
                    return value_span.text.strip() if value_span else None
                else:
                    return label_span.text.strip()
        except Exception as e:
            raise Exception(f"Error occurred when extracting text value for {html_element_tag} and text class name {text_class_filter} with label {text_class_filter}.\nException: {e}")
