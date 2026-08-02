from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import os

# Default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Python function to download kitten images
def download_images():
    urls = [
        "https://placekitten.com/200/300",
        "https://placekitten.com/250/350"
    ]
    output_dir = "/opt/airflow/dags/outputs"
    os.makedirs(output_dir, exist_ok=True)

    for i, url in enumerate(urls, start=1):
        response = requests.get(url)
        file_path = os.path.join(output_dir, f"kitten_{i}.jpg")
        with open(file_path, "wb") as f:
            f.write(response.content)
    print(f"Downloaded {len(urls)} kitten images to {output_dir}")

# Define DAG
with DAG(
    dag_id='Basic_AirFlow_Pipeline',
    default_args=default_args,
    schedule_interval=timedelta(days=1),
    catchup=False,
) as dag:

    # Task 1: Fetch kitten URLs (placeholder)
    fetch_kitten_urls = BashOperator(
        task_id='fetch_kitten_urls',
        bash_command="echo 'Fetching kitten URLs...'"
    )

    # Task 2: Download kitten images
    get_kitten_images = PythonOperator(
        task_id='get_kitten_images',
        python_callable=download_images
    )

    # Task 3: Write results to file
    write_results_to_file = BashOperator(
        task_id='write_results_to_file',
        bash_command="echo 'Results written to file!' > /opt/airflow/dags/outputs/results.txt"
    )

    # Task 4: Pipeline completion notification
    pipeline_notification = BashOperator(
        task_id='pipeline_notification',
        bash_command="echo 'Pipeline completed successfully!' > /opt/airflow/dags/outputs/kitten_state.txt"
    )

    # Define dependencies
    fetch_kitten_urls >> get_kitten_images >> write_results_to_file >> pipeline_notification
