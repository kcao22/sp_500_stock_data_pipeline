import pendulum
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from apps import af_utils
from apps.data_source_utils import yahoo_finance_utils, yahoo_finance_config


@dag(
    dag_id=af_utils.get_dag_name(dag_file_path=__file__),
    default_args=af_utils.get_default_args(),
    start_date=pendulum.datetime(year=2025, month=1, day=11),
    schedule="0 19 * * *",
    catchup=False,
    tags=["data_source: yahoo", "schedule: daily"],
    params={
        "companies": Param(
            default="",
            type="string",
            description="A comma separated string representation of company symbols to webscrape data for in case of backfills or failed scrapes."
        )
    }
)
def dag():
    """
    Web scrapes daily data for all companies listed in yahoo_finance_config's SP_500_SYMBOLS_CONFIG list or for all companies in the companies parameter.
    """
    @task
    def get_daily_data():
        context = get_current_context()
        scraper = yahoo_finance_utils.YahooFinanceScraper()
        symbols = []

        if context["params"]["companies"]:
            symbols = context["params"]["companies"].split(",")
        else:
            symbols = list(yahoo_finance_config.SP_500_CONFIG.keys())

        return scraper.extract_companies_data(daily_or_weekly="daily", symbols=symbols)

    get_daily_data()


dag()
