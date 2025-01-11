FROM python:3.11
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt -c https://raw.githubusercontent.com/apache/airflow/constraints-2.10.3/constraints-3.11.txt
