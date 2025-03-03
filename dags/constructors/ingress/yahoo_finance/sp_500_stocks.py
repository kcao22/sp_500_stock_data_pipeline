import pendulum
import time
from airflow.decorators import dag, task
from airflow.utils.task_group import TaskGroup
from airflow.models.baseoperator import chain
from apps import af_utils
from apps.data_source_utils import yahoo_finance_utils, yahoo_finance_config


@dag(
    dag_id=af_utils.get_dag_name(dag_file_path=__file__),
    default_args=af_utils.get_default_args(),
    start_date=pendulum.datetime(year=2025, month=1, day=11),
    schedule="0 19 * * *",
    catchup=False,
    tags=["data_source: yahoo", "schedule: daily"],
)
def dag():

    @task
    def get_daily_data(symbol: str):
        scraper = yahoo_finance_utils.YahooFinanceScraper()
        scraper.extract_daily_data(symbol=symbol)

    task_groups = []

    for company in yahoo_finance_config.SP_500_CONFIG:
        company_symbol = company["symbol"]
        with TaskGroup(group_id=company_symbol) as tg:
            get_daily_data(symbol=company_symbol)
        task_groups.append(tg)
        time.sleep(1)

    chain(*task_groups)


dag()
