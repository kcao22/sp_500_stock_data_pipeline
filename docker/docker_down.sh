echo "Tearing down dev env container..."
docker compose --file ./dev_env/docker-compose.yml down -v

echo "Tearing down Airflow containers..."
docker compose --file ./airflow/docker-compose.yml down -v

echo "Tearing down Airflow containers..."
docker compose --file ./spark/docker-compose.yml down -v

echo "Pruning unused volumes..."
docker system prune --volumes -f &
