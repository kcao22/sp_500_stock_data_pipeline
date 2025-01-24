FROM python:3.11
RUN apt-get update \
    && apt-get install -y --no-install-recommends
WORKDIR /usr/app/dbt/star
RUN pip install --upgrade pip
RUN pip install dbt-core==1.9.1 dbt-postgres==1.9.0
