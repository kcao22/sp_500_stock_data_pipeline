import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def create_postgres_engine(user: str, password: str, server: str, port: int, db: str, is_test: bool):
    """
    Creates a SQLAlchemy engine for connecting to local postgres warehouse.
    """
    return create_engine(
        url=f"{'postgresql' if is_test else 'redshift'}+psycopg2://{user}:{password}@{server}:{port}/{db}"
    )

def create_postgres_connection(is_test: bool):
    """
    Creates a connection to the Postgres database.
    @return: psycopg2 connection object.
    """

    engine = create_postgres_engine(
        user=os.getenv("POSTGRES_USER") if is_test else os.getenv("REDSHIFT_USER"),
        password=os.getenv("POSTGRES_PASSWORD") if is_test else os.getenv("REDSHIFT_PASSWORD"),
        server=os.getenv("POSTGRES_SERVER") if is_test else os.getenv("REDSHIFT_SERVER"),
        port=os.getenv("POSTGRES_PORT") if is_test else os.getenv("REDSHIFT_PORT"),
        db=os.getenv("POSTGRES_DB") if is_test else os.getenv("REDSHIFT_DB")
    )
    try:
        session = sessionmaker(bind=engine)
        return session()
    except Exception as e:
        raise Exception(f"Failed to create Postgres connection with Exception: {e}") from e


def execute_query(query: str, is_test: bool):
    session = create_postgres_connection(is_test=is_test)
    try:
        session.execute(query)
        session.commit()
    except Exception as e:
        raise Exception(f"Failed to execute query: {query} with Exception: {e}") from e
    finally:
        session.close()

def load_file_to_table(file_path: str, target_schema: str, target_table: str, copy_options: list, is_test):
    if is_test:
        try:
            information_schema_query = f"""
                SELECT
                    column_name
                FROM 
                    INFORMATION_SCHEMA.COLUMNS
                WHERE
                    table_schema = {target_schema}
                    AND table_name = {target_table}
                ORDER BY 
                    ordinal_position ASC
            """
            columns = execute_query(
                query=information_schema_query,
                is_test=is_test
            )
            column_names =",".joi([column[0] for column in columns])
            copy_query = f"""
                COPY {target_schema}.{target_table} ({column_names})
                FROM '{file_path}'
                f{'\n'.join(copy_option for copy_option in copy_options)}
            """
            execute_query(
                query=copy_query,
                is_test=is_test
            )
        except Exception as e:
            raise Exception(f"Failed to load file to {target_schema}.{target_table} with Exception: {e}") from e

def ingress_to_ods(operation: str, source_schema: str, source_table: str, target_schema: str, target_table: str, is_test: bool):
    if operation == "insert":
        try:
            insert_query = f"""
                INSERT INTO {target_schema}.{target_table}
                SELECT * FROM {source_schema}.{source_table}
            """
            execute_query(
                query=insert_query,
                is_test=is_test
            )
        except Exception as e:
            raise Exception(f"Failed to insert data from {source_schema}.{source_table} to {target_schema}.{target_table} with Exception: {e}") from e
    elif operation == "replace":
        try:
            delete_query = f"""
                DELETE FROM {target_schema}.{target_table};
            """
            execute_query(
                query=delete_query,
                is_test=is_test
            )
            insert_query = f"""
                INSERT INTO {target_schema}.{target_table}
                SELECT * FROM {source_schema}.{source_table}
            """
            execute_query(
                query=insert_query,
                is_test=is_test
            )
        except Exception as e:
            raise Exception(f"Failed to replace data in {target_schema}.{target_table} with Exception: {e}") from e
    elif operation == "upsert":
        try:
            
            upsert_query = f"""
                UPDATE {target_schema}.{target_table} AS target
                SET column_name = source.column_name
                FROM {source_schema}.{source_table} AS source
                WHERE target.id = source.id
            """
            execute_query(
                query=update_query,
                is_test=is_test
            )
        except Exception as e:
            raise Exception(f"Failed to update data in {target_schema}.{target_table} with Exception: {e}") from e
    else:
        raise ValueError(f"Invalid operation: {operation}. Must be either 'insert' or 'update'.")