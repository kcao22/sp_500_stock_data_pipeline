echo "Tearing down dev env container..."
docker compose --file ./dev_env/docker-compose.yml  --env-file .env down -v

echo "Tearing down Airflow containers..."
docker compose --file ./airflow/docker-compose.yml  --env-file .env down -v

echo "Tearing down AWS localstack containers..."
docker compose --file ./aws/docker-compose.yml  --env-file .env down

echo "Tearing down dbt containers..."
docker compose --file ./dbt/docker-compose.yml  --env-file .env down -v

echo "Tearing down Spark containers..."
docker compose --file ./spark/docker-compose.yml  --env-file .env down -v

echo "Tearing down Kafka containers..."
docker compose --file ./kafka/docker-compose.yml  --env-file .env down -v

echo "Tearing down streaming containers..."
docker compose --file ./streaming/docker-compose.yml --env-file .env down -v

echo "Pruning unused volumes..."
docker system prune --volumes -f &
