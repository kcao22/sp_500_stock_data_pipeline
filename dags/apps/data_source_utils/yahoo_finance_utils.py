import pandas
import pendulum
import time
from typing import Dict, List

from apps import s3
from apps.webscraper_utils import BeautifulSoupScraper
from apps.data_source_utils import yahoo_finance_config


class YahooFinanceScraper(BeautifulSoupScraper):
    def __init__(self):
        self.config = yahoo_finance_config
        super().__init__()

    def test_get_data(self, url: str):
        return super().request_webpage(
            url="https://finance.yahoo.com/quote/GOOGL/profile/"
        )

    def _get_data(self, url: str) -> Dict:
        """
        Extracts a single company's data based on the url argument.
        @param url: The yahoo finance URL for a company's stock. Should follow a format of https://finance.yahoo.com/quote/{sp_500_symbol}/
        @return: A dictionary mapping the specified config target keys to corresponding values extracted from the URL.
        """
        soup = super().request_webpage(url=url)
        data_record = {}
        extract_config = (
            self.config.DIM_DATA_EXTRACT_CONFIG
            if url.endswith("profile/")
            else self.config.DAILY_EXTRACT_CONFIG
        )
        for field_config in extract_config:
            try:
                data_value = None
                if field_config.get("is_data_value"):
                    data_value = super().get_element_data_value(
                        soup_object=soup,
                        html_element_tag=field_config.get("html_element_tag"),
                        identifier_attribute=field_config.get("identifier_attribute"),
                        identifier_value=field_config.get("identifier_value"),
                    )
                elif field_config.get("is_text_value"):
                    data_value = super().get_element_text_value(
                        soup_object=soup,
                        html_element_tag=field_config.get("html_element_tag"),
                        text_class_name=field_config.get("text_class_name"),
                        text_class_filter=field_config.get("text_class_filter"),
                        sibling_html_element_value_tag=field_config.get(
                            "sibling_html_element_value_tag"
                        ),
                        sibling_html_element_value_class=field_config.get(
                            "sibling_html_element_value_class"
                        ),
                        is_nested=field_config.get("is_nested_text_value"),
                    )
                else:
                    raise ValueError(
                        f"Unspecified config value type for config target key: {field_config.get('target_field')}"
                    )
                print(f"{field_config.get('target_field')}: {data_value}")
                data_record[field_config.get("target_field")] = data_value
            except Exception as e:
                raise Exception(
                    f"Get value for {field_config.get('target_field')} for {url} failed with Exception: {e}"
                ) from e
        return data_record

    def extract_daily_data(self) -> List:
        """
        Extracts daily data for all companies listed in yahoo_finance_config's SP_500_SYMBOLS_CONFIG list.
        @return: None
        """
        daily_data = []
        file_path = f"/data_sources/yahoo_finance/daily_sp_500/{pendulum.now().format('YYYYMMDD-HHmmss')}/sp_500_daily_{pendulum.now().format('YYYYMMDD')}.csv"
        for company_config in self.config.SP_500_CONFIG:
            daily_data.append(
                self._get_data(url=f"https://finance.yahoo.com/quote/{company_config.get('symbol')}/")
            )
            time.sleep(1)
        df = pandas.DataFrame(daily_data)
        s3.put_object(
            is_test=True,
            target_bucket="s3_ingress",
            key=file_path,
            body=df.to_csv(index=False)
        )
        return file_path

    def extract_dim_data(self) -> List:
        """
        Extracts dimension table data for all companies listed in yahoo_finance_config's SP_500_SYMBOLS_CONFIG list.
        @return: None
        """
        dim_data = []
        file_path = f"/data_sources/yahoo_finance/weekly_sp_500/{pendulum.now().format('YYYYMMDD-HHmmss')}/sp_500_weekly_{pendulum.now().format('YYYYMMDD')}.csv"
        for company_config in self.config.SP_500_CONFIG:
            dim_data.append(
                self._get_data(
                    url=f"https://finance.yahoo.com/quote/{company_config.get('symbol')}/profile/"
                )
            )
            time.sleep(1)
        df = pandas.DataFrame(dim_data)
        s3.put_object(
            is_test=True,
            target_bucket="s3_ingress",
            key=file_path,
            body=df.to_csv(index=False)
        )
        return file_path
