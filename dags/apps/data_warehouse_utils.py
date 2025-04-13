import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def create_postgres_engine(user: str, password: str, server: str, port: int, db: str):
    """
    Creates a SQLAlchemy engine for connecting to local postgres warehouse.
    """
    return create_engine(
        url=f"postgresql+psycopg2://{user}:{password}@{server}:{port}/{db}"
    )


def create_postgres_connection():
    """
    Creates a connection to the Postgres database.
    @return: psycopg2 connection object.
    """

    engine = create_postgres_engine(
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        server=os.getenv("POSTGRES_SERVER"),
        port=os.getenv("POSTGRES_PORT"),
        db=os.getenv("POSTGRES_DB")
    )
    try:
        session = sessionmaker(bind=engine)
        return session()
    except Exception as e:
        raise Exception(f"Failed to create Postgres connection with Exception: {e}") from e


def execute_query(query: str):
    session = create_postgres_connection()
    try:
        session.execute(query)
        session.commit()
    except Exception as e:
        raise Exception(f"Failed to execute query: {query} with Exception: {e}") from e
    finally:
        session.close()
