# Databricks notebook source
from pyspark.sql.functions import col, explode, explode_outer, to_timestamp
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
df_athlete_silver = (
    df_athlete_bronze.select(*simple_cols)
    .withColumn("created_at", to_timestamp("created_at"))
    .withColumn("updated_at", to_timestamp("updated_at"))
)
df_athlete_silver.write.format("delta").mode("overwrite").saveAsTable(
    "strava_catalog.silver.athlete"
)


# COMMAND ----------

# Bikes
df_bikes_silver = df_athlete_bronze.select(
    col("id").alias("athlete_id"), explode("bikes").alias("bike")
).select("athlete_id", "bike.*")
df_bikes_silver.write.format("delta").mode("overwrite").saveAsTable(
    "strava_catalog.silver.athlete_bike"
)

# COMMAND ----------

# Clubs
df_clubs_tot = df_athlete_bronze.select(
    col("id").alias("athlete_id"), explode("clubs").alias("club")
).select("athlete_id", "club.*")

df_club_silver = df_clubs_tot.drop(
    "athlete_id", "activity_types", "dimensions", "admin", "membership", "owner"
).dropDuplicates(["id"])
df_club_silver.write.format("delta").mode("overwrite").saveAsTable(
    "strava_catalog.silver.club"
)

# Club activity types
df_club_activity_type_silver = (
    df_clubs_tot.select(
        col("id").alias("club_id"),
        explode_outer("activity_types").alias("activity_type"),
    )
).dropDuplicates(["club_id", "activity_type"])
df_club_activity_type_silver.write.format("delta").mode("overwrite").saveAsTable(
    "strava_catalog.silver.club_activity_type"
)

# Club dimensions
df_club_dimensions_silver = (
    df_clubs_tot.select(
        col("id").alias("club_id"), explode_outer("dimensions").alias("dimension")
    )
).dropDuplicates(["club_id", "dimension"])
df_club_dimensions_silver.write.format("delta").mode("overwrite").saveAsTable(
    "strava_catalog.silver.club_dimension"
)

df_athlete_clubs_silver = df_clubs_tot.select(
    col("id").alias("club_id"), "athlete_id", "admin", "membership", "owner"
)
df_athlete_clubs_silver.write.format("delta").mode("overwrite").saveAsTable(
    "strava_catalog.silver.athlete_club"
)

# COMMAND ----------

# Shoes
df_shoes_silver = df_athlete_bronze.select(
    col("id").alias("athlete_id"), explode("shoes").alias("shoe")
).select("athlete_id", "shoe.*")
df_shoes_silver.write.format("delta").mode("overwrite").saveAsTable(
    "strava_catalog.silver.athlete_shoe"
)
