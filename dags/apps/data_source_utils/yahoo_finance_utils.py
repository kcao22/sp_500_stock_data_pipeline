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
					html_element_tag=field_config.get("html_element_tag"),
					identifier_attribute=field_config.get("identifier_attribute"),
					identifier_value=field_config.get("identifier_value")
				)
			elif field_config.get("is_text_value"):
				data_value = super().get_element_text_value(
					soup_object=soup,
					html_element_tag=field_config.get("html_element_tag"),
					text_class_name=field_config.get("text_class_name"),
					text_class_filter=field_config.get("text_class_filter"),
					sibling_html_element_value_tag=field_config.get("sibling_html_element_class"),
					sibling_html_element_value_class=field_config.get("sibling_html_element_value_class"),
					is_nested=field_config.get("is_nested_text_value")
				)
			print(f"Data Value for field {field_config.get('target_field')}: {data_value}")
			data_record[field_config.get("target_field")] = data_value
			print(field_config)
