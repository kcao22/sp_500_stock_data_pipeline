import pendulum
from apps import af_utils
from apps.data_source_utils import yahoo_finance_utils
from airflow.decorators import dag, task


@dag(
    dag_id=af_utils.get_dag_name(dag_file_path=__file__),
    default_args=af_utils.get_default_args(),
    start_date=pendulum.datetime(year=2025, month=1, day=11),
    schedule="0 7 * * 7",
    catchup=False,
    tags=["data_source: yahoo", "schedule: weekly"],
)
def dag():

    @task
    def get_weekly_dim_data():
        scraper = yahoo_finance_utils.YahooFinanceScraper()
        scraper.extract_dim_data()

    get_weekly_dim_data()


dag()
