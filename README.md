# Project Overview: Airflow ETL Pipeline with Postgres and Open Meteo API Integration for Solar Radiation Data in Lagos, Nigeria

This project involves creating an ETL (Extract, Transform, Load) pipeline using Apache Airflow. The pipeline extracts solar radiation data from the Open Meteo API, transforms the data, and loads it into a Postgres database. The entire workflow is orchestrated by Airflow, a platform that allows scheduling, monitoring, and managing workflows.

The project leverages Docker to run Airflow and Postgres as services, ensuring an isolated and reproducible environment. We also utilize Airflow hooks and operators to handle the ETL process efficiently.

---

## Key Components of the Project:

### **Airflow for Orchestration:**
Airflow is used to define, schedule, and monitor the entire ETL pipeline. It manages task dependencies, ensuring that the process runs sequentially and reliably. The Airflow DAG (Directed Acyclic Graph) defines the workflow, which includes tasks like data extraction, transformation, and loading.

### **Postgres Database:**
A PostgreSQL database is used to store the extracted and transformed data. Postgres is hosted in a Docker container, making it easy to manage and ensuring data persistence through Docker volumes. We interact with Postgres using Airflow’s PostgresHook and PostgresOperator.

### **Open Meteo API (Solar Radiation Data):**
The external API used in this project is the Open Meteo API, which provides data about solar radiation and clear sky radiation. This data includes metadata such as latitude, longitude, solar radiation, and time. The solar radiation data used in this project is sourced specifically from Lagos, Nigeria.

```
host= "https://ensemble-api.open-meteo.com"
extra=
{
  "base_path": "/v1/ensemble",
  "query_string": "latitude=6.4541&longitude=3.3947&hourly=shortwave_radiation,direct_radiation,diffuse_radiation,direct_normal_irradiance,global_tilted_irradiance&timezone=auto"
}
```

---

## Objectives of the Project:

### **1. Extract Data:**
The pipeline extracts solar radiation data from the Open Meteo API on a scheduled basis (daily, in this case).

### **2. Transform Data:**
Transformations such as filtering or processing the API response are performed to ensure that the data is in a suitable format before being inserted into the database.

### **3. Load Data into Postgres:**
The transformed data is loaded into a Postgres database. The data can be used for further analysis, reporting, or visualization.

---

## Architecture and Workflow:
The ETL pipeline is orchestrated in Airflow using a DAG (Directed Acyclic Graph). The pipeline consists of the following stages:

### **1. Extract (E):**
- The SimpleHttpOperator is used to make HTTP GET requests to the Open Meteo API’s solar radiation endpoint.
- The response is in JSON format, containing fields like `latitude`, `longitude`, `time`, `solar_radiation`, and `clear_sky_radiation`.

### **2. Transform (T):**
- The extracted JSON data is processed in the transform task using Airflow’s TaskFlow API (with the `@task` decorator).
- This stage involves extracting relevant fields like `latitude`, `longitude`, `time`, `solar_radiation`, and `clear_sky_radiation` and ensuring they are in the correct format for the database.

### **3. Load (L):**
- The transformed data is loaded into a Postgres table using PostgresHook.
- If the target table doesn’t exist in the Postgres database, it is created automatically as part of the DAG using a create table task.

---

## Postgres Table Schema:
The table schema used for this project is as follows:

```sql
CREATE TABLE solar_radiation_data (
    id SERIAL PRIMARY KEY,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    time TIMESTAMP NOT NULL,
    solar_radiation FLOAT NOT NULL,
    clear_sky_radiation FLOAT
);
```

---

## Benefits and Use Cases:

1. **Astronomical Planning:** Identify locations and times with optimal clear sky conditions for stargazing or astrophotography.
2. **Solar Power Analysis:** Analyze solar radiation data for regions of interest.
3. **Educational Tools:** Create visualizations or reports showcasing solar radiation patterns and their significance.

---

## Technologies and Tools:
- **Apache Airflow:** For workflow orchestration.
- **PostgreSQL:** For data storage.
- **Docker:** For containerized services.
- **Open Meteo API:** For solar radiation data extraction.
- **Python:** For transformation logic and custom Airflow tasks.

### To view the Postgres database:
1. **Open DBeaver** and click **New Database Connection**.
2. Select **PostgreSQL** and click **Next**.
3. Enter connection details:  
   - **Host**: `localhost`  
   - **Port**: `5432`  
   - **Database**: Your DB name  
   - **Username**: Your PostgreSQL username  
   - **Password**: Your password  
4. Click **Test Connection** to verify.
5. Click **Finish**, and your connection appears in the **Database Navigator**.
6. Right-click the connection and choose **Open SQL Editor** to query your database.

---

This project demonstrates a robust approach to building ETL pipelines with real-world applications in astronomy, solar energy analysis, and more. The modular design ensures scalability and ease of maintenance.