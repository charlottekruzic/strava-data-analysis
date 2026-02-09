# Databricks notebook source
from pyspark.sql.functions import col, explode
from pyspark.sql.types import ArrayType, StructType

# COMMAND ----------

df_athlete_bronze = spark.read.table("strava_catalog.bronze.athlete")
# df_athlete_bronze.printSchema()
# df_athlete_bronze.display()

# COMMAND ----------

# Athlete
simple_cols = [
    field.name
    for field in df_athlete_bronze.schema.fields
    if not isinstance(field.dataType, (ArrayType, StructType))
]
df_athlete_silver = df_athlete_bronze.select(*simple_cols)
df_athlete_silver.write.format("delta").mode("overwrite").saveAsTable(
    "strava_catalog.silver.athlete"
)

# COMMAND ----------

# Bikes
df_bikes_silver = df_athlete_bronze.select(
    col("id").alias("athlete_id"), explode("bikes").alias("bike")
).select("athlete_id", "bike.*")
df_bikes_silver.write.format("delta").mode("overwrite").saveAsTable(
    "strava_catalog.silver.athlete_bikes"
)

# COMMAND ----------

# Clubs
df_clubs_silver = df_athlete_bronze.select(
    col("id").alias("athlete_id"), explode("clubs").alias("club")
).select("athlete_id", "club.*")
df_clubs_silver.write.format("delta").mode("overwrite").saveAsTable(
    "strava_catalog.silver.athlete_clubs"
)

# COMMAND ----------

# Shoes
df_shoes_silver = df_athlete_bronze.select(
    col("id").alias("athlete_id"), explode("shoes").alias("shoe")
).select("athlete_id", "shoe.*")
df_shoes_silver.write.format("delta").mode("overwrite").saveAsTable(
    "strava_catalog.silver.athlete_shoes"
)
