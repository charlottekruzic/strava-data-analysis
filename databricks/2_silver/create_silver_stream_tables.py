# Databricks notebook source
from pyspark.sql import functions as F

# COMMAND ----------

df_stream_bronze = spark.read.table("strava_catalog.bronze.stream")

# COMMAND ----------

keys = [
    "time",
    "distance",
    "latlng",
    "altitude",
    "heartrate",
    "cadence",
    "moving",
    "velocity_smooth",
    "grade_smooth",
]

df_activity_stream_silver = df_stream_bronze.select(
    F.col("id").alias("activity_id"),
    F.col("time.original_size").alias("original_size"),  # same for all columns
    F.col("time.resolution").alias("resolution"),  # same for all columns
    F.col("time.series_type").alias("series_type"),  # same for all columns
    *[F.col(f"{col}.data").alias(f"{col}") for col in keys],
)

# COMMAND ----------

df_activity_stream_silver.write.format("delta").mode("overwrite").saveAsTable(
    "strava_catalog.silver.activity_stream"
)
