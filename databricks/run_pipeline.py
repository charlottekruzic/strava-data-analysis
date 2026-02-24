# Databricks notebook source
notebooks = [
    "./0_setup/create_strava_catalog",
    "./1_bronze/create_bronze_tables",
    "./2_silver/create_silver_activity_tables",
    "./2_silver/create_silver_athlete_tables",
    "./2_silver/create_silver_stream_tables",
    "./3_gold/create_gold_tables",
]

for nb in notebooks:
    dbutils.notebook.run(nb, timeout_seconds=300)
