FROM python:3.11.11-bullseye
COPY /../requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
