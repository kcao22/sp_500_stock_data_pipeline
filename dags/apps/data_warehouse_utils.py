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
