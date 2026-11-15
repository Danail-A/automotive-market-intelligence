import shutil
from configparser import ConfigParser
import pandas as pd

from pathlib import Path

import psycopg2
from psycopg2 import sql

## Define the paths

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILES = PROJECT_DIR / "data_files"
UNPROCESSED = DATA_FILES / "files_for_ingestion"
PROCESSED = DATA_FILES / "processed_files"
FAILED = DATA_FILES / "failed_files"
CONFIGFILE = PROJECT_DIR / "config.ini"

### Necessary constants and variables


TABLE = "raw.autoscout_listings"
UNPROCESSED_FILES = list(UNPROCESSED.rglob("*.csv"))

### Useful functions


def extract_table_columns(files: list) -> list:
    try:
        df = pd.read_csv(files[0])
        list_of_columns = list(df.columns)
        list_of_columns = [columns.replace(" ", "_") for columns in list_of_columns]
        print(f"{len(list_of_columns)} columns found.")
        return list_of_columns
    except IndexError:
        print("There are no unprocessed files.")


def create_table(cur, list_of_columns: list, table_name: str) -> None:
    
    # Added a try and except clause as if there is no files this function will raise a TypeError.
    try:
        string_join = " TEXT, ".join(list_of_columns)
        string_join = string_join + " TEXT"
        cur.execute(f"""CREATE TABLE IF NOT EXISTS {table_name}
                    ({string_join}) """)
        print(f"Table {table_name} successfully created!")
    # This just lets the function continue in case a typeerror is raised. Not sure if this cannot be handled better.
    except TypeError:
        ...


def load_csv_to_psql(
    csv_file: Path,
    cur,
    table_name: str,
    # unprocessed_folder: dir,
    passed_folder: dir,
    failed_folder: dir,
):
    try:
        with open(csv_file, "r") as file:
            cur.copy_expert(f"COPY {table_name} FROM STDIN WITH CSV HEADER", file)
            print(f"loading {csv_file.name}...")
        shutil.move(csv_file, passed_folder)
    except (FileNotFoundError, PermissionError, OSError, psycopg2.errors.BadCopyFileFormat) as e:
        print(f"{csv_file.name} couldn't load successfully. Error: {e}")
        shutil.move(csv_file, failed_folder)


def main():

    ## Configs for PostgreSQL

    config = ConfigParser()
    config.read(CONFIGFILE)

    ## These variables are unnecessary but I believe they make it a bit more readable?

    psql_user = config["postgresql"]["user"]
    psql_database = config["postgresql"]["database"]
    psql_password = config["postgresql"]["password"]
    psql_host = config["postgresql"]["host"]
    psql_port = config["postgresql"]["port"]

    ### Connection to psql and data loading

    conn = psycopg2.connect(
        database=psql_database,
        user=psql_user,
        password=psql_password,
        host=psql_host,
        port=psql_port,
    )

    cursor = conn.cursor()

    create_table(cursor, extract_table_columns(UNPROCESSED_FILES), TABLE)

    rows_commited = 0
    for file in UNPROCESSED_FILES:
        df = pd.read_csv(file)
        file_rows = int(df.shape[0])
        load_csv_to_psql(file, cursor, TABLE, PROCESSED, FAILED)
        copied_rows = cursor.rowcount
        if file_rows == copied_rows:
            conn.commit()
            print(f"{file_rows} rows were in the file. {copied_rows} were loaded.")
            print(f"{file.name} commit to {TABLE}")
            rows_commited += file_rows
        else:
            conn.rollback()
            print(f"{file_rows} rows were in the file. {copied_rows} were loaded.")
            print(f"{file.name} was not commited to {TABLE} due to mismatch. Please check again!")
    print(f"{rows_commited} total rows were commited!")


    cursor.close()
    conn.close()



if __name__ == "__main__":
    main()


# TODO: Every file should say how many rows it has and store how many nulls it has per column. 
# We should check and compare how many rows have been ingested and missing values per column.
# We should compare the two things on a file level and commit the copy when we know the data is matching.