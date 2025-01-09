FROM bitnami/spark:3.5.3
COPY /../requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
