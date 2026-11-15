import shutil
from configparser import ConfigParser
import pandas as pd
from pathlib import Path
import psycopg2
import hashlib


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
EXAMPLE_FILE = Path(__file__).resolve().parent.parent / "split_files" / "part_1.csv"

### Useful functions


def extract_table_columns(file: list) -> tuple:
    try:
        df = pd.read_csv(file)
        list_of_columns = list(df.columns)
        list_of_columns = [columns.replace(" ", "_") for columns in list_of_columns]
        # print(f"{len(list_of_columns)} columns found.")
        return tuple(list_of_columns)
    except IndexError:
        print("There are no unprocessed files.")


def create_table(cur, list_of_columns: tuple, table_name: str) -> None:
    
    # Added a try and except clause as if there is no files this function will raise a TypeError.
    try:
        string_join = " TEXT, ".join(list_of_columns)
        string_join = string_join + " TEXT"
        cur.execute(f"""CREATE TABLE IF NOT EXISTS {table_name}
                    ({string_join}) """)
        print(f"Table {table_name} is ready for use!")
    # This just lets the function continue in case a typeerror is raised. Not sure if this cannot be handled better.
    except TypeError:
        ...


def load_csv_to_psql(
    csv_file: Path,
    cur,
    table_name: str,
):
    try:
        with open(csv_file, "r") as file:
            cur.copy_expert(f"COPY {table_name} FROM STDIN WITH CSV HEADER", file)
            print(f"loading {csv_file.name}...")
    except (FileNotFoundError, PermissionError, OSError, psycopg2.errors.BadCopyFileFormat) as e:
        print(f"{csv_file.name} couldn't load successfully. Error: {e}")


def compute_hash_file(file_path: Path, algorithm='sha256'):

    # Here we will compute the hash of a file in chunks of 8192 bytes
    hash_func = hashlib.new(algorithm)

    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):
            hash_func.update(chunk)

    return hash_func.hexdigest()


def log_metadata():
    ...


def validate_file():
    ...


def main():

    MANDATORY_STRUCTURE = extract_table_columns(EXAMPLE_FILE)

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

    create_table(cursor, MANDATORY_STRUCTURE, TABLE)

    rows_commited = 0
    if not UNPROCESSED_FILES:
        print("There are no unprocessed files.")
    else:        
        for file in UNPROCESSED_FILES:
                ## Check column structure and if it matches the mandatory structure
            df = pd.read_csv(file)
            file_columns = tuple(df.columns)
            file_rows = int(df.shape[0])

            load_csv_to_psql(file, cursor, TABLE)
            copied_rows = cursor.rowcount

            if file_columns == MANDATORY_STRUCTURE:
                if file_rows == copied_rows:
                    conn.commit()
                    print(f"{file_rows} rows were in the file. {copied_rows} were loaded.")
                    print(f"{file.name} commit to {TABLE}")
                    rows_commited += file_rows
                    shutil.move(file, PROCESSED)
                    print(f"{file.name} has been moved to [processed_files]")
                else:
                    conn.rollback()
                    print(f"{file_rows} rows were in the file. {copied_rows} were loaded.")
                    print(f"{file.name} was not commited to {TABLE} due to mismatch. Please check again!")
                    shutil.move(file, FAILED)
                    print(f"{file.name} has been moved to [failed_files]")
            else:
                conn.rollback()
                print(f"{file.name}'s columns do not match the mandatory structure. Commit has been rolled back.")
                shutil.move(file, FAILED)
                print(f"{file.name} has been moved to [failed_files]")
        print(f"{rows_commited} total rows were commited!")


    cursor.close()
    conn.close()



if __name__ == "__main__":
    main()


# TODO: Need to implement the logging table in the db. 
# To be used to see if a certain file has already been copied regardles off file name. Hashes.
