from apps.webscraper_utils import BeautifulSoupScraper
from apps.data_source_utils import yahoo_finance_config

class yahoo_finance_scraper(BeautifulSoupScraper):
	def __init__(self, url: str):
		self.url = url
		self.config = yahoo_finance_config
		super().__init__(self.url)

	def test_get_data(self):
		return super().request_webpage(url=self.url)
	# def generate_daily_sp_500_excel_file(self):

	def get_dim_data(self):
		pass

	def get_daily_data(self):
		data_records = []
		soup = super().request_webpage(url=self.url)
		data_record = {}
		for field_config in self.config.DAILY_EXTRACT_CONFIG:
			data_value = None
			if field_config.get("is_data_value"):
				data_value = super().get_element_data_value(
					soup_object=soup,
					html_element_tag=field_config.get("element"),
					identifier_attribute=field_config.get("identifier_attribute"),
					identifier_value=field_config.get("identifier_value")
				)
			else:
				data_value = super().get_element_text_value(
					soup_object=soup,
					html_element_tag=field_config.get("element"),
					text_class_name=field_config.get("text_class")
				)
			print(f"Data Value for field {field_config.get('target_field')}: {data_value}")
			data_record[field_config.get("target_field")] = data_value
			print(field_config)
