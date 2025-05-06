import pandas
import pendulum
import time
from typing import Dict

from apps import s3
from apps.print_utils import print_logging_info_decorator
from apps.webscraper_utils import BeautifulSoupScraper
from apps.data_source_utils import yahoo_finance_config


class YahooFinanceScraper(BeautifulSoupScraper):
    def __init__(self):
        self.config = yahoo_finance_config
        self.timestamp_str = pendulum.now(tz="UTC").format("YYYYMMDD-HHmmss")
        self.today_timestamp_str = pendulum.now().start_of("day").format("YYYYMMDD-HHmmss")
        super().__init__()

    def _get_data(self, symbol: str, scope: str) -> Dict:
        """
        Extracts a single company's data based on the company's stock name and scope (daily data or weekly dim data).
        @param symbol: The company's stock identifier. 
        @param scope: The scope of the extract - either daily or weekly.

        @return: A dictionary mapping the specified config target keys to corresponding values extracted from the URL.
        """
        url = f"https://finance.yahoo.com/quote/{symbol}/{'profile/' if scope == 'weekly' else ''}"
        soup = super().request_webpage(url=url)
        data_record = {"symbol": symbol, "load_timestamp_utc": self.today_timestamp_str}
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

    @print_logging_info_decorator
    def extract_companies_data(self, daily_or_weekly: str, symbols: list, is_test: bool) -> str:
        """
        Extracts daily data for all companies listed in yahoo_finance_config's SP_500_SYMBOLS_CONFIG list.
        :param daily_or_weekly: String representation of if daily extract of data or weekly extract of data.
        :param symbols: List of symbols to extract daily data for.
        @return: File path of extracted data.
        """
        scope = ""
        if daily_or_weekly.lower() not in ("daily", "weekly"):
            raise ValueError(
                f"Invalid daily_or_weekly argument value: {daily_or_weekly}. Must be either 'daily' or 'weekly'."
            )
        else:
            scope = daily_or_weekly.lower()

        file_path = f"/data_sources/yahoo_finance/{scope}/{self.timestamp_str}/{scope}_{self.today_timestamp_str}.csv"
        companies_data = []
        for symbol in symbols:
            companies_data.append(self._get_data(symbol=symbol, scope=scope))
            time.sleep(2)
        df = pandas.DataFrame(companies_data)
        s3.put_object(
            is_test=is_test,
            bucket="s3_ingress",
            key=file_path,
            body=df.to_csv(index=False).encode()
        )
        return file_path
