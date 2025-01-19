from apps.webscraper_utils import BeautifulSoupScraper


class yahoo_finance_scraper(BeautifulSoupScraper):
	def __init__(self, url: str):
		self.url = url
		super().__init__(self.url)

	def test_get_data(self):
		return super().request_webpage(url=self.url)
	# def generate_daily_sp_500_excel_file(self):
