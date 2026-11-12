import csv
import re
import os
import shutil
from configparser import ConfigParser

from pathlib import Path

import psycopg2
from psycopg2 import sql

## File excercises

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILES = PROJECT_DIR / "data_files"
UNPROCESSED = DATA_FILES / "files_for_ingestion"
PROCESSED = DATA_FILES / "processed_files"
FAILED = DATA_FILES / "failed_files"

unprocessed_files = UNPROCESSED.rglob("*.csv")

def load_csv_to_psql(csv_file, cur, table_name):
    ## make it check first if a table is already created and if not create one and then execute this again.
    try:
        with open(csv_file, 'r') as file:
            cur.copy_expert(f"COPY {table_name} FROM STDIN WITH CSV HEADER", file)
            print(f"{csv_file} loaded successfully.")
        shutil.move(UNPROCESSED, PROCESSED)
    except (FileNotFoundError, PermissionError, OSError) as e:
        print(f"{csv_file} couldn't load successfully. Error: {e}")
        shutil.move(UNPROCESSED, FAILED)


## Configs for PostgreSQL

configfile = PROJECT_DIR / "config.ini"

config = ConfigParser()

config.read(configfile)

psql_user = config['postgresql']['user']
psql_database = config['postgresql']['database']
psql_password = config['postgresql']['password']
psql_host = config['postgresql']['host']
psql_port = config['postgresql']['port']

### Connection to psql

conn = psycopg2.connect(
    database=psql_database,
    user=psql_user,
    password=psql_password,
    host=psql_host,
    port=psql_port
)

cursor = conn.cursor()
table = "raw.autoscout_listings"
cursor.execute(f"SELECT * FROM {table}")
data = cursor.fetchall()



# for file in unprocessed_files:
#     load_csv_to_psql(file, cursor, table)


conn.close()