import os

from apps.print_utils import print_logging_info_decorator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@print_logging_info_decorator(redacted_params=["user", "password"])
def create_postgres_engine(
    user: str, password: str, server: str, port: int, db: str, is_test: bool
):
    """
    Creates a SQLAlchemy engine for connecting to local postgres warehouse.
    """
    return create_engine(
        url=f"{'postgresql' if is_test else 'redshift'}+psycopg2://{user}:{password}@{server}:{port}/{db}"
    )


@print_logging_info_decorator
def create_postgres_connection(is_test: bool):
    """
    Creates a connection to the Postgres database.
    @return: psycopg2 connection object.
    """
    user = os.getenv("POSTGRES_USER") if is_test else os.getenv("REDSHIFT_USER")
    password = (
        os.getenv("POSTGRES_PASSWORD") if is_test else os.getenv("REDSHIFT_PASSWORD")
    )
    server = os.getenv("POSTGRES_SERVER") if is_test else os.getenv("REDSHIFT_SERVER")
    port = os.getenv("POSTGRES_PORT") if is_test else os.getenv("REDSHIFT_PORT")
    db = os.getenv("POSTGRES_DB") if is_test else os.getenv("REDSHIFT_DB")

    # Print statements for debugging
    print(f"{'TEST' if is_test else 'PRODUCTION'} ENVIRONMENT:")
    print(f"User: {user}")
    print(f"Password: {'[REDACTED]'}")  # Avoid printing sensitive information
    print(f"Server: {server}")
    print(f"Port: {port}")
    print(f"Database: {db}")

    engine = create_postgres_engine(
        user=user,
        password=password,
        server="data-warehouse",
        port=5432,
        db=db,
        is_test=is_test,
    )
    try:
        session = sessionmaker(bind=engine)
        return session()
    except Exception as e:
        raise Exception(
            f"Failed to create Postgres connection with Exception: {e}"
        ) from e


@print_logging_info_decorator
def execute_query(query: str, expect_returns: bool, is_test: bool):
    session = create_postgres_connection(is_test=is_test)
    try:
        result = session.execute(query)
        session.commit()
        if expect_returns:
            return result.fetchall()
        else:
            return
    except Exception as e:
        raise Exception(f"Failed to execute query: {query} with Exception: {e}") from e
    finally:
        session.close()


@print_logging_info_decorator
def load_file_to_table(
    file_path: str,
    target_schema: str,
    target_table: str,
    copy_options: list,
    redshift_copy_options: list,
    is_test: bool,
):
    try:
        information_schema_query = f"""
            SELECT
                column_name
            FROM 
                INFORMATION_SCHEMA.COLUMNS
            WHERE
                table_schema = '{target_schema}'
                AND table_name = '{target_table}'
            ORDER BY 
                ordinal_position ASC
        """
        columns = execute_query(
            query=information_schema_query, expect_returns=True, is_test=is_test
        )
        column_names = ",\n".join([column[0] for column in columns])
        copy_options = "\n,".join(copy_option for copy_option in copy_options)
        redshift_copy_options = "\n,".join(
            redshift_copy_option for redshift_copy_option in redshift_copy_options
        )
        file_path = (
            file_path if is_test else f"s3://prod_data_warehouse_archive/{file_path}"
        )
        copy_query = f"""
            COPY {target_schema}.{target_table} ({column_names})
            FROM '{file_path}'
        """
        if is_test:
            copy_query += f"""
                \nWITH (
                    {copy_options}
                );
            """
        else:
            copy_query += f"""
                \n{redshift_copy_options}
            """
        execute_query(query=copy_query, expect_returns=False, is_test=is_test)
    except Exception as e:
        raise Exception(
            f"Failed to load file to {target_schema}.{target_table} with Exception: {e}"
        ) from e


@print_logging_info_decorator
def ingress_to_ods(
    operation: str,
    source_schema: str,
    source_table: str,
    target_schema: str,
    target_table: str,
    primary_key: list,
    is_test: bool,
):
    if operation == "append":
        try:
            insert_query = f"""
                INSERT INTO {target_schema}.{target_table}
                SELECT * FROM {source_schema}.{source_table}
            """
            execute_query(query=insert_query, expect_returns=False, is_test=is_test)
        except Exception as e:
            raise Exception(
                f"Failed to insert data from {source_schema}.{source_table} to {target_schema}.{target_table} with Exception: {e}"
            ) from e
    elif operation == "replace":
        try:
            delete_query = f"""
                DELETE FROM {target_schema}.{target_table};
            """
            execute_query(query=delete_query, expect_returns=False, is_test=is_test)
            insert_query = f"""
                INSERT INTO {target_schema}.{target_table}
                SELECT * FROM {source_schema}.{source_table}
            """
            execute_query(query=insert_query, expect_returns=False, is_test=is_test)
        except Exception as e:
            raise Exception(
                f"Failed to replace data in {target_schema}.{target_table} with Exception: {e}"
            ) from e
    elif operation == "upsert":
        merge_condition = ""
        primary_keys = ",".join([f"'{key}'" for key in primary_key])
        primary_key_query = f"""
            SELECT
                column_name,
                data_type,
                character_maximum_length,
                numeric_precision,
                numeric_scale
            FROM
                INFORMATION_SCHEMA.COLUMNS
            WHERE 
                column_name IN ({primary_keys})
                and table_schema = '{target_schema}'
                and table_name = '{target_table}'
        """
        primary_key_data = execute_query(
            query=primary_key_query,
            expect_returns=True,
            is_test=is_test
        )
        for i, row in enumerate(primary_key_data):
            col = row[0]
            data_type = row[1]
            char_max_length = row[2]
            numeric_precision = row[3]
            numeric_scale = row[4]
            source_col_cast = _get_cast_logic(
                column=col,
                data_type=data_type,
                char_max_length=char_max_length,
                numeric_precision=numeric_precision,
                numeric_scale=numeric_scale,
                is_test=is_test
            )
            merge_condition += f"target.{col} = {source_col_cast}"
            merge_condition += f"{' AND ' if i != len(primary_key_data) - 1 else ''}"
        try:
            information_schema_query = f"""
                SELECT
                    column_name,
                    data_type,
                    character_maximum_length,
                    numeric_precision,
                    numeric_scale
                FROM 
                    INFORMATION_SCHEMA.COLUMNS
                WHERE
                    table_schema = '{target_schema}'
                    AND table_name = '{target_table}'
                ORDER BY 
                    ordinal_position ASC
            """
            columns_data = execute_query(
                query=information_schema_query, expect_returns=True, is_test=is_test
            )
            cols = ""
            match_logic = ""
            no_match_logic = ""
            for i, row in enumerate(columns_data):
                col = row[0]
                data_type = row[1]
                char_max_length = row[2]
                numeric_precision = row[3]
                numeric_scale = row[4]
                cols += f"{col}{',\n' if i != len(columns_data) - 1 else ''}"
                match_logic += _get_match_logic(
                    column=col,
                    data_type=data_type,
                    char_max_length=char_max_length,
                    numeric_precision=numeric_precision,
                    numeric_scale=numeric_scale,
                    is_test=is_test,
                )
                match_logic += f"{',\n' if i != len(columns_data) - 1 else ''}"
                no_match_logic += _get_cast_logic(
                    column=col,
                    data_type=data_type,
                    char_max_length=char_max_length,
                    numeric_precision=numeric_precision,
                    numeric_scale=numeric_scale,
                    is_test=is_test,
                )
                no_match_logic += f"{',\n' if i != len(columns_data) - 1 else ''}"
            upsert_query = f"""
            MERGE INTO 
                {target_schema}.{target_table} AS target 
                USING {source_schema}.{source_table} AS source
            ON
                {merge_condition}
            WHEN MATCHED THEN
                UPDATE SET
                    {match_logic}
            WHEN NOT MATCHED THEN
                INSERT ({cols})
                VALUES ({no_match_logic})
            """
            execute_query(query=upsert_query, expect_returns=False, is_test=is_test)
        except Exception as e:
            raise Exception(
                f"Failed to update data in {target_schema}.{target_table} with Exception: {e}"
            ) from e
    else:
        raise ValueError(
            f"Invalid operation: {operation}. Must be either 'append', 'replace' or 'update'."
        )


def _get_match_logic(
    column: str,
    data_type: str,
    char_max_length: int,
    numeric_precision: int,
    numeric_scale: int,
    is_test: bool,
) -> str:
    """
    Returns the match logic for the given column based on its data type.
    """
    if data_type == "character varying":
        return f"{column} = source.{column}::character varying({char_max_length})"
    elif data_type == "numeric":
        return f"{column} = source.{column}::numeric({numeric_precision},{numeric_scale})"
    elif "timestamp" in data_type:
        return f"{column} = source.{column}::timestamp"
    elif data_type == "jsonb":
        return f"{column} = source.{column}::{'jsonb' if is_test else 'super'}"
    else:
        return f"{column} = source.{column}::{data_type}"


def _get_cast_logic(
    column: str,
    data_type: str,
    char_max_length: int,
    numeric_precision: int,
    numeric_scale: int,
    is_test: bool,
) -> str:
    """
    Returns the cast logic for the given column based on its data type.
    """
    if data_type == "character varying":
        return f"source.{column}::character varying({char_max_length})"
    elif data_type == "numeric":
        return f"source.{column}::numeric({numeric_precision},{numeric_scale})"
    elif "timestamp" in data_type:
        return f"source.{column}::timestamp"
    elif data_type == "jsonb":
        return f"source.{column}::{'jsonb' if is_test else 'super'}"
    else:
        return f"source.{column}::{data_type}"
