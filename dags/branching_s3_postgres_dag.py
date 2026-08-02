from airflow import DAG
from airflow.operators.python import BranchPythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.amazon.aws.operators.s3 import S3CreateObjectOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime

def check_s3_file(**kwargs):
    s3 = S3Hook(aws_conn_id="aws_default")
    bucket = "bucket-name"
    key = "path/to/file.ext"
    
    if s3.check_for_key(key, bucket_name=bucket):
        return "insert_sql"   # file exists → go to Postgres
    else:
        return "create_object"  # file missing → create it in S3

with DAG(
    dag_id="branching_s3_postgres_dag",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
) as dag:

    py_branch_task = BranchPythonOperator(
        task_id="branch_python",
        python_callable=check_s3_file,
        provide_context=True,
    )

    s3_create_object_task = S3CreateObjectOperator(
        task_id="create_object",
        s3_bucket="bucket-name",
        s3_key="path/to/file.ext",
        data="Some default content",
        replace=True,
    )

    insert_sql_task = PostgresOperator(
        task_id="insert_sql",
        sql="""
            INSERT INTO table_name (column1, column2, column3)
            VALUES ('value1', 'value2', 'value3');
        """,
        postgres_conn_id="postgres_connection_id",
        autocommit=True,
    )

    final_task = DummyOperator(task_id="final")

    py_branch_task >> [s3_create_object_task, insert_sql_task]
    [s3_create_object_task, insert_sql_task] >> final_task
