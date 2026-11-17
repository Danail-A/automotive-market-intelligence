import shutil
from configparser import ConfigParser
import pandas as pd
from pathlib import Path
import psycopg2
import hashlib
import datetime


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


def extract_table_columns(file: Path) -> tuple:
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
        print(f"Table {table_name} has issues. Please check!")


def load_csv_to_psql(
    csv_file: Path,
    connection,
    cur,
    table_name: str,
) -> None:
    try:
        with open(csv_file, "r") as file:
            cur.copy_expert(f"COPY {table_name} FROM STDIN WITH CSV HEADER", file)
            print(f"loading {csv_file.name}...")
    except (FileNotFoundError, PermissionError, OSError, psycopg2.errors.BadCopyFileFormat) as e:
        print(f"{csv_file.name} couldn't load successfully. Error: {e}")
        connection.rollback()
        cur.close
    except psycopg2.errors.InFailedSqlTransaction as e:
        print(f"There are no values inside the table yet. Error: {e}")
        connection.rollback()
        cur.close
    except psycopg2.errors.CharacterNotInRepertoire as e:
        print(f"{csv_file.name} file contains symbols that are not supported. Error: {e}")
        connection.rollback()
        cur.close



def compute_hash_file(file_path: Path, algorithm='sha256') -> str:

    # Here we will compute the hash of a file in chunks of 8192 bytes
    hash_func = hashlib.new(algorithm)

    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):
            hash_func.update(chunk)

    return hash_func.hexdigest()


def load_imported_files_for_check(cur, columns: list, table_name: str) -> list[tuple]:

    try:
        string_join = ", ".join(columns)
        cur.execute(f"""SELECT {string_join}
                        FROM {table_name}
                        WHERE status = 'SUCCESS'""")
        query_output = cur.fetchall()
        instances = cur.rowcount
        print(f"{len(columns)} columns and {instances} rows have been loaded.")
        return query_output
    except psycopg2.errors.InFailedSqlTransaction as e:
        print(f"There are no values inside the table yet. Error: {e}")


def validate_file(loaded_files: list[tuple], value_to_compare: str) -> bool:

    try:
        result = [row[0] for row in loaded_files]
        if value_to_compare in result:
            print("The file has already been processed and loaded.")
            return False
        else:
            print("File has not been processed before. Continue...")
            return True
    except TypeError:
        print(f"There are no values inside the table. Proceed...")
        return True


def add_metadata_values(cur, list_of_values: list, table_name: str) -> None:
        string_join = "', '".join(list_of_values)
        string_join = "'" + string_join + "'"
        cur.execute(f"""INSERT INTO {table_name}
                        VALUES ({string_join})""")
        # for value in list_of_values:
        #     print(value)


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

    ## Check if the tables are ready.

    create_table(cursor, MANDATORY_STRUCTURE, TABLE)
    create_table(cursor, list_of_columns=("file_hash", "file_name", "status", "rows_loaded", "processed_at"), table_name="raw.metadata_ingestion_log")
    conn.commit()

    rows_commited = 0
    if not UNPROCESSED_FILES:
        print("There are no unprocessed files.")
    else:        
        for file in UNPROCESSED_FILES:
            
            ## Compute the hash
            file_hash = compute_hash_file(file)
            file_name = str(file.name)

            ## Load the metadata of the file that have already been loaded.
            imported_files = load_imported_files_for_check(
            cur=cursor,
            columns=["file_hash"],
            table_name="raw.metadata_ingestion_log")

            ## Check column structure and if it matches the mandatory structure
            df = pd.read_csv(file)
            file_columns = extract_table_columns(file)
            file_rows = int(df.shape[0])

            ## Execute the logic. First check if the file has been processed before. 
            ## Second check is to see if the structure is the needed structure for copy.
            ## Then check if all the rows have been copied before commiting.

            if validate_file(imported_files, file_hash):
                if file_columns == MANDATORY_STRUCTURE:
                    load_csv_to_psql(file, conn, cursor, TABLE)
                    copied_rows = cursor.rowcount
                    if file_rows == copied_rows:
                        conn.commit()
                        print(f"{file_rows} rows were in the file. {copied_rows} were loaded.")
                        print(f"{file_name} commit to {TABLE}")
                        rows_commited += file_rows
                        try:
                            shutil.move(file, PROCESSED)
                        except shutil.Error:
                            print("File already exists in destination.")
                        print(f"{file_name} has been moved to [processed_files]")
                        status = "SUCCESS"
                        copied_rows = str(copied_rows)
                    else:
                        conn.rollback()
                        print(f"{file_rows} rows were in the file. {copied_rows} were loaded.")
                        print(f"{file_name} was not commited to {TABLE} due to mismatch. Please check again!")
                        try:
                            shutil.move(file, FAILED)
                        except shutil.Error:
                            print("File already exists in destination.")
                        print(f"{file_name} has been moved to [failed_files]")
                        status = "FAILED"
                        copied_rows = "0"
                else:
                    print(f"{file_name}'s columns do not match the mandatory structure.")
                    try:
                        shutil.move(file, FAILED)
                    except shutil.Error:
                        print("File already exists in destination.")
                    print(f"{file_name} has been moved to [failed_files]")
                    status = "FAILED"
                    copied_rows = "0"
            else:
                try:
                    shutil.move(file, FAILED)
                except shutil.Error:
                    print("File already exists in destination.")
                print(f"{file_name} has been moved to [failed_files]")
                status = "FAILED/PROCESSED"
                copied_rows = "0"

            timestamp = str(datetime.datetime.now())
            add_metadata_values(cursor, 
                                table_name="raw.metadata_ingestion_log",
                                list_of_values=[file_hash, file_name, str(status), copied_rows, timestamp])
            print("A record has been added to the metadata folder.")
            conn.commit()

        print(f"{rows_commited} total rows were commited!")


    cursor.close()
    conn.close()



if __name__ == "__main__":
    main()