# Databricks notebook source
from pyspark.sql.functions import regexp_extract

# COMMAND ----------

json_files_path = '/Volumes/strava_catalog/raw/json_files'

# COMMAND ----------

# DBTITLE 1,Untitled
df_athlete = spark.read.json(f'{json_files_path}/athlete.json')
df_athlete.write.format('delta').mode('overwrite').saveAsTable('strava_catalog.bronze.athlete')

# COMMAND ----------

df_activity_summary = spark.read.json(f"{json_files_path}/activities.json")
df_activity_summary.write.format("delta").mode("overwrite").saveAsTable(
    "strava_catalog.bronze.activity_summary"
)

# COMMAND ----------

df_activity = spark.read.json(f'{json_files_path}/activity/*.json')
df_activity.write.format('delta').mode('overwrite').saveAsTable('strava_catalog.bronze.activity')

# COMMAND ----------

df_stream = spark.read.json(f'{json_files_path}/streams/*.json')
df_stream = df_stream.withColumn(
    'id',
    regexp_extract('_metadata.file_path', r'([0-9]+)_streams\.json$',1)
)
df_stream.write.format('delta').mode('overwrite').saveAsTable('strava_catalog.bronze.stream')