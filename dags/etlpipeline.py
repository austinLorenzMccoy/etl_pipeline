from airflow import DAG
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.decorators import task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.dates import days_ago
import json

# Define the DAG
with DAG(
    dag_id='solar_radiation_ingestion',
    start_date=days_ago(1),
    schedule_interval='@daily',
    catchup=False,
) as dag:

    # Step 1: Create the table if it doesn't exist
    @task
    def create_table():
        pg_hook = PostgresHook(postgres_conn_id='postgres_connection')
        create_table_query = """
            CREATE TABLE IF NOT EXISTS solar_radiation_data (
                id SERIAL PRIMARY KEY,
                latitude FLOAT NOT NULL,
                longitude FLOAT NOT NULL,
                time TIMESTAMP NOT NULL,
                shortwave_radiation FLOAT,
                direct_radiation FLOAT,
                diffuse_radiation FLOAT,
                direct_normal_irradiance FLOAT,
                global_tilted_irradiance FLOAT
            );
        """
        pg_hook.run(create_table_query)

    # Step 2: Extract the data from the API
    extract_data = SimpleHttpOperator(
        task_id='extract_data',
        http_conn_id='solar_radiation_api',
        endpoint='v1/ensemble',
        method='GET',
        data={
            "latitude": 6.4541,
            "longitude": 3.3947,
            "hourly": [
                "shortwave_radiation",
                "direct_radiation", 
                "diffuse_radiation",
                "direct_normal_irradiance",
                "global_tilted_irradiance"
            ],
            "timezone": "auto"
        },
        response_filter=lambda response: json.loads(response.text),
        log_response=True
    )

    # Step 3: Transform the data
    @task
    def transform_data(data):
        transformed_data = []

        # Extract data arrays
        times = data['hourly']['time']
        shortwave = data['hourly']['shortwave_radiation']
        direct = data['hourly']['direct_radiation']
        diffuse = data['hourly']['diffuse_radiation']
        direct_normal = data['hourly']['direct_normal_irradiance']
        global_tilted = data['hourly']['global_tilted_irradiance']

        # Transform each data point
        for i in range(len(times)):
            transformed_data.append({
                'latitude': data['latitude'],
                'longitude': data['longitude'],
                'time': times[i],
                'shortwave_radiation': shortwave[i] if isinstance(shortwave[i], (int, float)) else shortwave[i][0],
                'direct_radiation': direct[i] if isinstance(direct[i], (int, float)) else direct[i][0],
                'diffuse_radiation': diffuse[i] if isinstance(diffuse[i], (int, float)) else diffuse[i][0],
                'direct_normal_irradiance': direct_normal[i] if isinstance(direct_normal[i], (int, float)) else direct_normal[i][0],
                'global_tilted_irradiance': global_tilted[i] if isinstance(global_tilted[i], (int, float)) else global_tilted[i][0]
            })

        return transformed_data

    # Step 4: Load the data into the PostgreSQL database
    @task
    def load_data(data):
        pg_hook = PostgresHook(postgres_conn_id='postgres_connection')
        insert_query = """
            INSERT INTO solar_radiation_data (
                latitude, longitude, time, shortwave_radiation, direct_radiation,
                diffuse_radiation, direct_normal_irradiance, global_tilted_irradiance
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        for record in data:
            pg_hook.run(insert_query, parameters=[
                record['latitude'],
                record['longitude'],
                record['time'],
                record['shortwave_radiation'],
                record['direct_radiation'],
                record['diffuse_radiation'],
                record['direct_normal_irradiance'],
                record['global_tilted_irradiance']
            ], autocommit=True)

    # Step 5: Define task dependencies
    create_table_task = create_table()
    transform_task = transform_data(extract_data.output)
    load_task = load_data(transform_task)

    create_table_task >> extract_data >> transform_task >> load_task
