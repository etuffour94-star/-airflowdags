from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime, timedelta
import requests
import os

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Python function: fetch kitten URLs
def fetch_urls(**context):
    urls = [
        "https://placekitten.com/200/300",
        "https://placekitten.com/250/350"
    ]
    # Push URLs into XCom so downstream tasks can use them
    context['ti'].xcom_push(key='kitten_urls', value=urls)

# Python function: download images
def download_images(**context):
    urls = context['ti'].xcom_pull(key='kitten_urls', task_ids='fetch_kitten_urls')
    output_dir = "/opt/airflow/dags/outputs"
    os.makedirs(output_dir, exist_ok=True)

    paths = []
    for i, url in enumerate(urls, start=1):
        response = requests.get(url)
        file_path = os.path.join(output_dir, f"kitten_{i}.jpg")
        with open(file_path, "wb") as f:
            f.write(response.content)
        paths.append(file_path)

    # Push file paths into XCom
    context['ti'].xcom_push(key='image_paths', value=paths)

# Python function: prepare results for Postgres
def prepare_results(**context):
    paths = context['ti'].xcom_pull(key='image_paths', task_ids='get_kitten_images')
    # Return SQL insert statement dynamically
    sql_statements = [
        f"INSERT INTO kitten_images (file_path, created_at) VALUES ('{p}', NOW());"
        for p in paths
    ]
    return " ".join(sql_statements)

with DAG(
    dag_id='Production_Kitten_Pipeline',
    default_args=default_args,
    schedule_interval=timedelta(days=1),
    catchup=False,
) as dag:

    # Task 1: Fetch URLs
    fetch_kitten_urls = PythonOperator(
        task_id='fetch_kitten_urls',
        python_callable=fetch_urls,
        provide_context=True
    )

    # Task 2: Download images
    get_kitten_images = PythonOperator(
        task_id='get_kitten_images',
        python_callable=download_images,
        provide_context=True
    )

    # Task 3: Insert results into Postgres
    insert_results = PostgresOperator(
        task_id='insert_results',
        postgres_conn_id='airflow_postgres',  # must match your Airflow connection
        sql="{{ task_instance.xcom_pull(task_ids='prepare_sql') }}"
    )

    # Task 3a: Prepare SQL dynamically
    prepare_sql = PythonOperator(
        task_id='prepare_sql',
        python_callable=prepare_results,
        provide_context=True
    )

    # Task 4: Pipeline completion notification
    pipeline_notification = BashOperator(
        task_id='pipeline_notification',
        bash_command="echo 'Pipeline completed successfully!' > /opt/airflow/dags/outputs/kitten_state.txt"
    )

    # Dependencies
    fetch_kitten_urls >> get_kitten_images >> prepare_sql >> insert_results >> pipeline_notification
