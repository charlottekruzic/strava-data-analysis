# Databricks notebook source
# MAGIC %sql
# MAGIC --Create catalog structure
# MAGIC CREATE CATALOG IF NOT EXISTS strava_catalog;
# MAGIC CREATE SCHEMA IF NOT EXISTS strava_catalog.raw;
# MAGIC CREATE SCHEMA IF NOT EXISTS strava_catalog.bronze;
# MAGIC CREATE SCHEMA IF NOT EXISTS strava_catalog.silver;
# MAGIC CREATE SCHEMA IF NOT EXISTS strava_catalog.gold;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Create volume for raw JSON files
# MAGIC CREATE VOLUME IF NOT EXISTS strava_catalog.raw.json_files
