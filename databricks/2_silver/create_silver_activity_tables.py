# Databricks notebook source
from pyspark.sql import functions as F

# COMMAND ----------

df_activity_bronze = spark.read.table("strava_catalog.bronze.activity")

# COMMAND ----------

# Table activity
df_activity_silver = (
    df_activity_bronze.withColumn("athlete_id", F.col("athlete.id"))
    .withColumn("end_lat", F.col("end_latlng")[0])
    .withColumn("end_lng", F.col("end_latlng")[1])
    .withColumn("gear_id", F.col("gear.id"))
    .withColumn("map_id", F.col("map.id"))
    .withColumn("photo_count", F.col("photos.count"))
    .withColumn("start_lat", F.col("start_latlng")[0])
    .withColumn("start_lng", F.col("start_latlng")[1])
    .withColumn("start_date", F.to_timestamp("start_date"))
    .withColumn("start_date_local", F.to_timestamp("start_date_local"))
    .drop(
        "athlete",
        "available_zones",
        "best_efforts",
        "end_latlng",
        "gear",
        "laps",
        "map",
        "photos",
        "segment_efforts",
        "similar_activities",
        "splits_metric",
        "splits_standard",
        "start_latlng",
        "stats_visibility",
    )
)

columns = df_activity_bronze.select(F.col("stats_visibility.type")).first().type

df_stats_visibility = (
    df_activity_bronze.select("id", F.explode("stats_visibility").alias("stat"))
    .select(
        F.col("id"),
        F.col("stat.type").alias("stat_type"),
        F.col("stat.visibility").alias("stat_visibility"),
    )
    .groupBy("id")
    .pivot("stat_type", columns)
    .agg(F.first("stat_visibility"))
)

df_stats_visibility = df_stats_visibility.select(
    "id",
    *[
        F.col(c).alias(f"{c}_visibility")
        for c in df_stats_visibility.columns
        if c != "id"
    ],
)

df_activity_silver = df_activity_silver.join(df_stats_visibility, "id", "left")
df_activity_silver = df_activity_silver.select(sorted(df_activity_silver.columns))
df_activity_silver.write.format("delta").mode("overwrite").saveAsTable(
    "strava_catalog.silver.activity"
)

# COMMAND ----------

# Table activity_best_effort
df_activity_best_effort_silver = df_activity_bronze.select(
    F.explode("best_efforts").alias("effort")
).select("effort.*")

df_activity_best_effort_silver = (
    df_activity_best_effort_silver.withColumn("activity_id", F.col("activity.id"))
    .withColumn("athlete_id", F.col("athlete.id"))
    .withColumn("start_date", F.to_timestamp("start_date"))
    .withColumn("start_date_local", F.to_timestamp("start_date_local"))
    .drop("achievements", "activity", "athlete")
)

df_activity_best_effort_silver = df_activity_best_effort_silver.select(
    sorted(df_activity_best_effort_silver.columns)
)
df_activity_best_effort_silver.write.format("delta").mode("overwrite").saveAsTable(
    "strava_catalog.silver.activity_best_effort"
)

# COMMAND ----------

# Table activity_best_effort_achievement
df_activity_best_effort_achievement_silver = (
    df_activity_bronze.select(F.explode("best_efforts").alias("effort"))
    .select(
        F.col("effort.id").alias("best_efforts_id"),
        F.explode("effort.achievements").alias("achievement"),
    )
    .select("best_efforts_id", "achievement.*")
)

df_activity_best_effort_achievement_silver.write.format("delta").mode(
    "overwrite"
).saveAsTable("strava_catalog.silver.activity_best_effort_achievement")

# COMMAND ----------

# Table gear
df_gear_silver = (
    df_activity_bronze.filter(F.col("gear").isNotNull())
    .select("gear.*")
    .dropDuplicates(["id"])
)
df_gear_silver.write.format("delta").mode("overwrite").saveAsTable(
    "strava_catalog.silver.gear"
)

# COMMAND ----------

# Table activity_lap
df_activity_lap_silver = (
    df_activity_bronze.select(F.explode("laps").alias("lap"))
    .select("lap.*")
    .withColumn("activity_id", F.col("activity.id"))
    .withColumn("athlete_id", F.col("athlete.id"))
    .withColumn("start_date", F.to_timestamp("start_date"))
    .withColumn("start_date_local", F.to_timestamp("start_date_local"))
    .drop("activity", "athlete")
)

df_activity_lap_silver = df_activity_lap_silver.select(
    sorted(df_activity_lap_silver.columns)
)
df_activity_lap_silver.write.format("delta").mode("overwrite").saveAsTable(
    "strava_catalog.silver.activity_lap"
)

# COMMAND ----------

# Table activity_map
df_activity_map_silver = df_activity_bronze.select("map.*")
df_activity_map_silver.write.format("delta").mode("overwrite").saveAsTable(
    "strava_catalog.silver.activity_map"
)

# COMMAND ----------

# Table activity_photo
df_activity_photo_silver = (
    df_activity_bronze.select(
        F.col("id").alias("activity_id"),
        "photos.count",
        "photos.primary.*",
        "photos.use_primary_photo",
    )
    .withColumn("url_100", F.col("urls").getItem("100"))
    .withColumn("url_600", F.col("urls").getItem("600"))
    .drop("urls")
)

df_activity_photo_silver.write.format("delta").mode("overwrite").saveAsTable(
    "strava_catalog.silver.activity_photo"
)

# COMMAND ----------

# Table activity_segment_effort
df_activity_segment_effort_silver = (
    df_activity_bronze.select(F.explode("segment_efforts").alias("segment_effort"))
    .select("segment_effort.*")
    .withColumn("activity_id", F.col("activity.id"))
    .withColumn("athlete_id", F.col("athlete.id"))
    .withColumn("segment_id", F.col("segment.id"))
    .withColumn("start_date", F.to_timestamp("start_date"))
    .withColumn("start_date_local", F.to_timestamp("start_date_local"))
    .drop("achievements", "activity", "athlete", "segment")
)

df_activity_segment_effort_silver = df_activity_segment_effort_silver.select(
    sorted(df_activity_segment_effort_silver.columns)
)
df_activity_segment_effort_silver.write.format("delta").mode("overwrite").saveAsTable(
    "strava_catalog.silver.activity_segment_effort"
)

# COMMAND ----------

# Table segment
df_segment_silver = (
    df_activity_bronze.select(F.explode("segment_efforts").alias("segment_effort"))
    .select("segment_effort.segment.*")
    .withColumn("end_lat", F.col("end_latlng")[0])
    .withColumn("end_lng", F.col("end_latlng")[1])
    .withColumn("start_lat", F.col("start_latlng")[0])
    .withColumn("start_lng", F.col("start_latlng")[1])
    .drop("end_latlng", "start_latlng")
    .dropDuplicates(["id"])
)

df_segment_silver = df_segment_silver.select(sorted(df_segment_silver.columns))
df_segment_silver.write.format("delta").mode("overwrite").saveAsTable(
    "strava_catalog.silver.segment"
)

# COMMAND ----------

# Table activity_segment_effort_achievement
df_activity_segment_effort_achievement_silver = (
    df_activity_bronze.select(F.explode("segment_efforts").alias("effort"))
    .select(
        F.col("effort.id").alias("segment_efforts_id"),
        F.explode("effort.achievements").alias("achievement"),
    )
    .select("segment_efforts_id", "achievement.*")
)

df_activity_segment_effort_achievement_silver.write.format("delta").mode(
    "overwrite"
).saveAsTable("strava_catalog.silver.activity_segment_effort_achievement")

# COMMAND ----------

# Table activity_similar_activity
trend_columns = df_activity_bronze.select("similar_activities.trend.*").columns

df_activity_similar_activity_silver = (
    df_activity_bronze.select(F.col("id").alias("activity_id"), "similar_activities.*")
    .select(
        "*", *[F.col(f"trend.{col}").alias(f"trend_{col}") for col in trend_columns]
    )
    .drop("trend")
)

df_activity_similar_activity_silver = df_activity_similar_activity_silver.select(
    sorted(df_activity_similar_activity_silver.columns)
)
df_activity_similar_activity_silver.write.format("delta").mode("overwrite").saveAsTable(
    "strava_catalog.silver.activity_similar_activity"
)

# COMMAND ----------

# Table activity_split_metric
df_activity_split_metric_silver = df_activity_bronze.select(
    F.col("id").alias("activity_id"), F.explode("splits_metric").alias("split_metric")
).select("activity_id", "split_metric.*")

df_activity_split_metric_silver.write.format("delta").mode("overwrite").saveAsTable(
    "strava_catalog.silver.activity_split_metric"
)

# COMMAND ----------

# Table split_standard
df_activity_split_standard_silver = df_activity_bronze.select(
    F.col("id").alias("activity_id"),
    F.explode("splits_standard").alias("split_standard"),
).select("activity_id", "split_standard.*")

df_activity_split_standard_silver.write.format("delta").mode("overwrite").saveAsTable(
    "strava_catalog.silver.activity_split_standard"
)
