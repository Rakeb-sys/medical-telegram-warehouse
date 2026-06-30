# medical-telegram-warehouse
Shipping a Data Product: From Raw Telegram Data to an Analytical API

Here is a comprehensive, production-ready `README.md` that consolidates all 5 tasks into a clear, professional project layout.

---

# 🏥 Medical Telegram Data Warehouse & Analytics Platform

An end-to-end ELT data platform designed for **Kara Solutions** to extract, transform, enrich, and expose insights from public Ethiopian medical Telegram channels (`CheMed`, `Lobelia Cosmetics`, `Tikvah Pharma`, and other platforms via `et.tgstat.com/medicine`).

This system integrates a custom async data scraper, a structured PostgreSQL warehouse layer, **dbt** transformations, a **YOLOv8** computer vision asset classifier, a **FastAPI** REST presentation engine, and full workflow orchestration via **Dagster**.

---

## 🏗️ System Architecture & Data Flow

The platform decouples collection from analysis, flowing sequentially across five distinct layers:

1. **Extract & Load (Task 1):** Python + Telethon scrapes messages and images asynchronously, saving raw files to a time-partitioned Data Lake.
2. **Warehouse Loading & dbt (Task 2):** Raw JSONs are bulk-loaded into PostgreSQL and modeled into an analytical **Star Schema** with robust testing rules.
3. **Computer Vision Enrichment (Task 3):** Downloaded images are passed through a YOLOv8 network to classify promotional styles and append objects back into the data warehouse.
4. **Analytical REST API (Task 4):** A fast microservice layer built with SQLAlchemy and Pydantic exposes query-optimized reporting endpoints.
5. **Orchestration (Task 5):** A self-healing Dagster graph schedules, retries, and monitors the entire architecture end-to-end.

---

## 📂 Project Directory Structure

```text
medical-telegram-warehouse/
├── api/                       # Task 4: FastAPI REST Layer
│   ├── database.py            # SQLAlchemy database engine connection pool
│   ├── main.py                # REST API endpoints & route logic
│   └── schemas.py             # Pydantic request/response validation contracts
├── data/                      # File-Based Local Data Lake
│   └── raw/
│       ├── images/            # Organized media partitions: /{channel_name}/{msg_id}.jpg
│       └── telegram_messages/ # Chronological batch partitions: /{YYYY-MM-DD}/{channel}.json
├── logs/                      # System operation & extraction activity logs
├── models/                    # Task 2 & 3: dbt Dimensional Models
│   ├── staging/               # stg_telegram_messages view definitions
│   └── marts/                 # dim_channels, dim_dates, fct_messages, fct_image_detections
├── src/                       # Central Operational Source Code Scripts
│   ├── load_to_postgres.py    # Python DB bulk ingestion script
│   ├── pipeline.py            # Task 5: Central Dagster orchestration mapping
│   ├── scraper.py             # Task 1: Async Telethon collector
│   └── yolo_detect.py         # Task 3: YOLOv8 image classifier
├── tests/                     # dbt Custom Data Validation Assertions
│   ├── assert_no_future_messages.sql
│   └── assert_positive_views.sql
├── dbt_project.yml            # dbt operational properties profile
└── profiles.yml               # dbt target connection database driver mappings

```

---

## 🚀 Step-by-Step Environment Setup & Running Instuctions

### 1. Prerequisites & Database Provisioning

Ensure you have Python 3.10+ and a running instance of PostgreSQL. Open your SQL terminal/pgAdmin and execute:

```sql
CREATE DATABASE telegram_warehouse;
-- Connect to the database and generate the target staging landing zone
CREATE SCHEMA raw;

```

### 2. Dependency Installation

Clone this repository, initialize a virtual environment, and install the comprehensive task framework extensions:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic ultralytics dbt-postgres dagster dagster-webserver telethon pandas numpy

```

### 3. Step 1: Run the Telegram Scraper (Task 1)

Ensure you have registered your application details at `my.telegram.org` to generate your `API_ID` and `API_HASH` tokens.

```bash
python src/scraper.py

```

* **Output:** Populates chronological raw JSON frames into `data/raw/telegram_messages/` and downloads images to `data/raw/images/`.

### 4. Step 2: Push Data & Execute Transformations (Task 2 & 3)

Bulk insert raw unstructured entries and trigger the data factory compilation layer:

```bash
# Ingest JSON fields into postgres raw schema
python src/load_to_postgres.py

# Execute YOLOv8 image processing and classification
python src/yolo_detect.py

# Run dbt transformations & tests
dbt debug --profiles-dir .
dbt run --profiles-dir .
dbt test --profiles-dir .

```

### 5. Step 3: Run the FastAPI Application (Task 4)

Boot up the secure presentation framework:

```bash
uvicorn api.main:app --reload

```

* **Interactive OpenAPI Docs:** Navigate to `http://127.0.0.1:8000/docs` to execute requests live against the data warehouse.

### 6. Step 4: Launch the Pipeline Orchestrator (Task 5)

Automate all scripts under an interactive management UI:

```bash
dagster-webserver -f src/pipeline.py

```

* **Dashboard Monitor:** Open `http://localhost:3000` to visualize data lineages, configure error retry cycles, or toggle the 1 AM daily automated run schedule.

---

## 📊 Analytical Data Models (Star Schema Core)

dbt structures your incoming text rows into an analytics-optimized dimensional footprint:

* **`dim_channels`**: Keeps master tracking profiles for channels, defining entity sectors (*Pharmaceuticals*, *Cosmetics*, *Medical*) alongside rolled-up analytics metrics like average reach and total historical outputs.
* **`dim_dates`**: Deconstructs plain timestamps into temporal dimensions (`day_of_week`, `week_of_year`, `is_weekend`) for macro trend tracking.
* **`fct_messages`**: Central repository logging clean content attributes, content lengths, view thresholds, and forward activity rates.
* **`fct_image_detections`**: Enriches standard message facts by mapping identified YOLO visual objects (`detected_class`, `confidence_score`, `image_category`) straight into your analysis workspace via primary composite foreign keys.

---

## 🧪 Data Quality Control Framework

To prevent bad data from reaching downstream presentation tools, the following automated validation assertions are executed on every run:

1. **Native Field Integrity Rules:** `unique` and `not_null` properties are verified on all primary keys (`channel_key`, `date_key`, `message_id`).
2. **Referential Tracking Rules:** `relationships` assertions verify that foreign keys in fact sheets accurately point to real dimension records.
3. **Custom Business Constraints:** * `assert_no_future_messages.sql`: Rejects any records generated with system dates beyond the present execution clock.
* `assert_positive_views.sql`: Enforces logical baseline limits, flagging record changes that register traffic parameters below zero.