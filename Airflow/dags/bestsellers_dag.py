from datetime import timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import yaml

from scripts.bestsellers_script import run_zipfile_downloader, run_query_on_redshift


default_args = {
    'owner': 'bestsellers',
    'wait_for_downstream': False,
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': timedelta(seconds=30),
}

with DAG(
    dag_id='bestsellers_dag',
    default_args=default_args,
    schedule_interval='0 */8 * * *',
    start_date=days_ago(1),
    tags=['BESTSELLERS'],
    catchup=False,
    concurrency=16,
    max_active_runs=1,
) as dag:

    # configuration for each data source is described in the yml file
    with open("dags/yml/bestsellers_data_sources.yml", "r") as yaml_file:
        sources = yaml.safe_load(yaml_file)

    # this list holds insert_* tasks
    list_insert_data_to_redshift_tasks = []

    for source in sources:
        # download zip files and store them into S3
        run_zipfile_downloader_task = PythonOperator(
            task_id='download_' + source["name"],
            python_callable=run_zipfile_downloader,
            op_kwargs={
                "bucket_dir": source["bucket_dir"],
                "file_url": source["file_url"],
                "macros": {
                    "ts_nodash": "{{ ts_nodash }}",
                }
            },
            provide_context=True,
        )

        # Creating new partition for recently downloaded file
        # using Jinja filters to create partition key from ts_nodash
        partition_clause = f'{source["partition_key"]}=' + \
            "{% set sliced_ts_nodash = ts_nodash | string | replace('T', '') %}{{ sliced_ts_nodash[:10] }}"
        location = f'{source["bucket_dir"]}{partition_clause}/'
        sqls = [
            f"""
                ALTER TABLE {source["external_dbtable"]}
                ADD IF NOT EXISTS PARTITION({partition_clause})
                LOCATION '{location}';
            """,
        ]

        run_create_partition_on_redshift = PythonOperator(
            task_id='partition_' + source["name"],
            python_callable=run_query_on_redshift,
            op_kwargs={
                "sqls": sqls,
            },
            provide_context=True,
        )

        # inserting data into Redshift Cluster
        run_insert_data_to_redshift = PythonOperator(
            task_id='insert_' + source["name"],
            python_callable=run_query_on_redshift,
            op_kwargs={
                "sqls": [
                    f"""
                        INSERT INTO {source["dbtable"]}

                            WITH deduplicated_data AS (
                                SELECT {source["columns"]}
                                , row_number() OVER(PARTITION BY {source["distinct_on_columns"]}) AS row_number
                                FROM {source["external_dbtable"]}
                                WHERE {partition_clause}
                            )
                            , fresh_data AS (
                                SELECT {source["columns"]}
                                FROM deduplicated_data a
                                WHERE row_number = 1

                                EXCEPT

                                SELECT {source["columns"]}
                                FROM {source["dbtable"]} b
                            )

                        SELECT *
                        FROM fresh_data
                    """
                ],
            },
            provide_context=True,
        )
        list_insert_data_to_redshift_tasks.append(run_insert_data_to_redshift)

        run_zipfile_downloader_task >> run_create_partition_on_redshift >> run_insert_data_to_redshift

    # updating the materialized view to incluce fresh data
    run_refresh_materialized_view_on_redshift = PythonOperator(
        task_id='run_refresh_materialized_view_on_redshift',
        python_callable=run_query_on_redshift,
        op_kwargs={
            "sqls": [
                """
                    REFRESH MATERIALIZED VIEW bestsellers.review_joined_price
                """
            ],
        },
        provide_context=True,
    )

    for insert_task in list_insert_data_to_redshift_tasks:
        insert_task >> run_refresh_materialized_view_on_redshift
