# Databricks notebook source
# MAGIC %sql
# MAGIC CREATE TABLE IF NOT EXISTS strava_catalog.gold.dim_date (
# MAGIC   date_id DATE PRIMARY KEY,
# MAGIC   day INT,
# MAGIC   month INT,
# MAGIC   year INT,
# MAGIC   month_short VARCHAR(10)
# MAGIC );
# MAGIC
# MAGIC TRUNCATE TABLE strava_catalog.gold.dim_date;
# MAGIC
# MAGIC INSERT INTO
# MAGIC   strava_catalog.gold.dim_date WITH date_range AS (
# MAGIC     SELECT
# MAGIC       explode(
# MAGIC         sequence(
# MAGIC           to_date('2020-01-01'),
# MAGIC           to_date('2030-12-31'),
# MAGIC           interval 1 day
# MAGIC         )
# MAGIC       ) as date_id
# MAGIC   )
# MAGIC SELECT
# MAGIC   date_id,
# MAGIC   DAY(date_id) as day,
# MAGIC   MONTH(date_id) as month,
# MAGIC   YEAR(date_id) as year,
# MAGIC   DATE_FORMAT(date_id, 'MMM') as month_short
# MAGIC FROM
# MAGIC   date_range

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE TABLE IF NOT EXISTS strava_catalog.gold.dim_athlete(
# MAGIC   athlete_id BIGINT PRIMARY KEY,
# MAGIC   firstname VARCHAR(100),
# MAGIC   lastname VARCHAR(100),
# MAGIC   profile_url VARCHAR(500)
# MAGIC );
# MAGIC
# MAGIC TRUNCATE TABLE strava_catalog.gold.dim_athlete;
# MAGIC
# MAGIC INSERT INTO
# MAGIC   strava_catalog.gold.dim_athlete
# MAGIC SELECT
# MAGIC   id as athlete_id,
# MAGIC   firstname,
# MAGIC   lastname,
# MAGIC   profile as profile_url
# MAGIC FROM
# MAGIC   strava_catalog.silver.athlete

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE TABLE IF NOT EXISTS strava_catalog.gold.gold_run_activity (
# MAGIC   activity_id BIGINT PRIMARY KEY,
# MAGIC   athlete_id BIGINT,
# MAGIC   gear_id VARCHAR(50),
# MAGIC   date_id DATE,
# MAGIC   start_date_local TIMESTAMP,
# MAGIC   distance_km DOUBLE,
# MAGIC   moving_time_sec BIGINT,
# MAGIC   total_elevation_gain_m DOUBLE,
# MAGIC   start_lat DOUBLE,
# MAGIC   start_lng DOUBLE
# MAGIC );
# MAGIC
# MAGIC TRUNCATE TABLE strava_catalog.gold.gold_run_activity;
# MAGIC
# MAGIC INSERT INTO
# MAGIC   strava_catalog.gold.gold_run_activity
# MAGIC SELECT
# MAGIC   a.id AS activity_id,
# MAGIC   a.athlete_id,
# MAGIC   a.gear_id,
# MAGIC   CAST(a.start_date_local AS DATE) AS date_id,
# MAGIC   a.start_date_local,
# MAGIC   ROUND(a.distance / 1000, 2) AS distance_km,
# MAGIC   a.moving_time AS moving_time_sec,
# MAGIC   a.total_elevation_gain,
# MAGIC   a.start_lat,
# MAGIC   a.start_lng
# MAGIC FROM
# MAGIC   strava_catalog.silver.activity a
# MAGIC WHERE
# MAGIC   a.sport_type = 'Run'

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE TABLE IF NOT EXISTS strava_catalog.gold.gold_best_effort (
# MAGIC   gold_best_effort_id BIGINT PRIMARY KEY,
# MAGIC   activity_id BIGINT,
# MAGIC   distance_m BIGINT,
# MAGIC   distance_label VARCHAR(20),
# MAGIC   elapsed_time_sec BIGINT,
# MAGIC   start_date_local TIMESTAMP
# MAGIC );
# MAGIC
# MAGIC TRUNCATE TABLE strava_catalog.gold.gold_best_effort;
# MAGIC
# MAGIC INSERT INTO
# MAGIC   strava_catalog.gold.gold_best_effort
# MAGIC SELECT
# MAGIC   be.id AS gold_best_effort_id,
# MAGIC   be.activity_id,
# MAGIC   be.distance,
# MAGIC   be.name AS distance_label,
# MAGIC   be.elapsed_time AS elapsed_time_sec,
# MAGIC   be.start_date_local
# MAGIC FROM
# MAGIC   strava_catalog.silver.activity_best_effort be
# MAGIC   INNER JOIN strava_catalog.gold.gold_run_activity gra ON gra.activity_id = be.activity_id

# COMMAND ----------

# DBTITLE 1,Untitled
# MAGIC %sql
# MAGIC CREATE TABLE IF NOT EXISTS strava_catalog.gold.gold_gear_usage (
# MAGIC   gear_id VARCHAR(50) PRIMARY KEY,
# MAGIC   athlete_id BIGINT,
# MAGIC   gear_name VARCHAR(100),
# MAGIC   total_distance_km DOUBLE
# MAGIC );
# MAGIC
# MAGIC TRUNCATE TABLE strava_catalog.gold.gold_gear_usage;
# MAGIC
# MAGIC INSERT INTO
# MAGIC   strava_catalog.gold.gold_gear_usage
# MAGIC SELECT
# MAGIC   g.id AS gear_id,
# MAGIC   s.athlete_id,
# MAGIC   g.name AS gear_name,
# MAGIC   ROUND(SUM(gra.distance_km), 2) as total_distance_km
# MAGIC FROM
# MAGIC   strava_catalog.silver.gear g
# MAGIC   INNER JOIN strava_catalog.silver.athlete_shoe s ON g.id = s.id
# MAGIC   INNER JOIN strava_catalog.gold.gold_run_activity gra ON gra.gear_id = g.id
# MAGIC GROUP BY
# MAGIC   g.id,
# MAGIC   s.athlete_id,
# MAGIC   g.name
