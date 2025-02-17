import pendulum
from apps import af_utils
from apps.data_source_utils import yahoo_finance_utils
from airflow.decorators import dag, task

@dag(
    dag_id=af_utils.get_dag_name(dag_file_path=__file__),
    default_args=af_utils.get_default_args(),
    start_date=pendulum.datetime(year=2025, month=1, day=11),
    schedule=None,
    catchup=False
)
def dag():
    @task
    def test_get_google_site():
        scraper = yahoo_finance_utils.YahooFinanceScraper()
        response = scraper.test_get_data(url="https://finance.yahoo.com/quote/GOOGL/profile/")
        print(response.prettify())

    @task
    def test_get_daily_data():
        scraper = yahoo_finance_utils.YahooFinanceScraper()
        scraper._get_data(url="https://finance.yahoo.com/quote/GOOGL/")

    @task
    def test_get_dim_data():
        scraper = yahoo_finance_utils.YahooFinanceScraper()
        scraper._get_data(url="https://finance.yahoo.com/quote/GOOGL/profile/")

    test_get_google_site()
    test_get_daily_data()
    test_get_dim_data()


dag()
