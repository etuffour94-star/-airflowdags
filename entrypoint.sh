#!/bin/bash
set -e

# Initialize the Airflow database (only if not already initialized)
airflow db init

# Create an admin user if it doesn't exist
airflow users create \
  --username admin \
  --firstname Edward \
  --lastname Admin \
  --role Admin \
  --email admin@example.com \
  --password mysecurepassword || true

# Start the webserver
exec airflow webserver
