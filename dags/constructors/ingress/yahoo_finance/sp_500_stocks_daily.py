import pendulum
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from apps import af_utils, data_warehouse_utils, s3
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
        ),
        "is_test": Param(
            default=False,
            type="boolean",
            description="If True, then local. Else AWS prod environment."
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
        is_test = False

        if context["params"]["companies"]:
            symbols = context["params"]["companies"].split(",")
        else:
            symbols = [company.get("symbol") for company in yahoo_finance_config.SP_500_CONFIG]

        if context["params"]["is_test"]:
            is_test = context["params"]["is_test"]

        return scraper.extract_companies_data(is_test=is_test, daily_or_weekly="daily", symbols=symbols)

    @task
    def archive_daily_data(file_path: str):
        context = get_current_context()
        is_test = False
        if context["params"]["is_test"]:
            is_test = context["params"]["is_test"]
        s3.copy_object(
            is_test=is_test,
            source_bucket="s3_ingress",
            source_key=file_path,
            target_bucket="s3_archive",
            target_key=file_path
        )
        s3.delete_object(
            is_test=is_test,
            bucket="s3_ingress",
            key=file_path
        )
        return file_path

    @task
    def load_daily_data_to_ingress(file_path: str):
        context = get_current_context()
        is_test = False
        if context["params"]["is_test"]:
            is_test = context["params"]["is_test"]
        downloaded_file_path = s3.download_file(
            is_test=is_test,
            bucket="s3_ingress",
            key=file_path,
            filename=f"tmp/{file_path.split('/')[-1]}"
        )
        data_warehouse_utils.load_file_to_table(
            file_path=downloaded_file_path,
            target_schema="ingress",
            target_table="companies_daily",
        )

    @task
    def load_daily_data_to_ods():
        context = get_current_context()
        is_test = False
        if context["params"]["is_test"]:
            is_test = context["params"]["is_test"]
        data_warehouse_utils.ingress_to_ods(
            operation="upsert",
            source_schema="ingress",
            source_table="companies_daily",
            target_schema="ods",
            target_table="companies_daily",
            primary_key=["symbol", "load_timestamp_utc"],
            is_test=is_test
        )

    ingress_file_path = get_daily_data()
    archive_file_path = archive_daily_data(file_path=ingress_file_path)
    load_to_ingress = load_daily_data_to_ingress(file_path=archive_file_path)
    load_to_ingress >> load_daily_data_to_ods()


dag()
