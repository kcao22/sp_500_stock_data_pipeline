echo "Building dev env container"
docker compose --file ./dev_env/docker-compose.yml up

echo "Building Airflow containers..."
docker compose --file ./airflow/docker-compose.yml up

echo "Building Spark containers..."
docker compose --file ./spark/docker-compose.yml up
