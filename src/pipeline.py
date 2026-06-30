import pandas as pd
from pathlib import Path
import numpy as np
from dagster import op, graph, ScheduleDefinition, Definitions, RetryPolicy
from sqlalchemy import create_engine, Date, Text, Float
import os

# === Database setup ===
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "telegram_warehouse")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

@op(
    description = "Scrape telegram data",
    retry_policy = RetryPolicy(max_retries=2, delay=30)
)

def scrape_telegram_data() -> str:
    print("Extracting rows from CheMed, Lobelia, and Tikvah Pharma...")
    return "data/raw/telegram_messages"


@op(
    description = "Load JSON to database",
    retry_policy = RetryPolicy(max_retries=2, delay=30)
)

def load_raw_to_postgres(raw_data_dir: str) -> str:
    print(f"Loading files from {raw_data_dir} into raw.telegram_messages...")
    return "raw_loaded"

@op(
    description = "Execute dbt models",
    retry_policy = RetryPolicy(max_retries=2, delay=30)
)

def run_dbt_transformations(upstream_flag: str) -> str:
    print("Running dbt transformations (dim_channels, dim_dates, fct_messages)...")
    return "dbt_complete"

@op(
    description = "Run object detection",
    retry_policy = RetryPolicy(max_retries=2, delay=30)
)

def run_yolo_enrichment(upstream_flag: str) -> None:
    print("Running YOLOv8 image processing and updating image fact tables...")
    print("Pipeline execution cycle complete.")

@graph(description="Full Medical Warehouse ELT: Extract → Load → dbt Transform → YOLO Enrichment.")
def telegram_etl():
    """Full ETL: extract → transform → load."""
    # 1. Invoke scrape to get the raw data path string
    scraped_path = scrape_telegram_data()
    
    # 2. Pass the result into load by invoking it
    loaded_flag = load_raw_to_postgres(scraped_path)
    
    # 3. Pass that flag into dbt
    dbt_flag = run_dbt_transformations(loaded_flag)
    
    # 4. Pass the final flag into the YOLO step
    run_yolo_enrichment(dbt_flag)

# Create a job from the graph
telegram_etl_job = telegram_etl.to_job(name="telegram_etl_job")

# Schedule it to run every day at 1 AM
daily_schedule = ScheduleDefinition(
    name="daily_telegram_etl_schedule",
    job=telegram_etl, # Point directly to the compiled job
    cron_schedule="0 1 * * *", # Runs exactly at 01:00 AM every day
)

# IMPORTANT: Register your jobs and schedules with Definitions
defs = Definitions(
    jobs=[telegram_etl_job],
    schedules=[daily_schedule],
)