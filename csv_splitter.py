import csv
import os

# ===== CONFIGURATION =====
input_file = "autoscout24_dataset_20251108.csv"
output_folder = "split_files"
number_of_files = 30
# =========================

os.makedirs(output_folder, exist_ok=True)

# Count the total data rows (excluding the header)
with open(input_file, "r", newline="", encoding="utf-8-sig") as f:
    total_rows = sum(1 for _ in f) - 1

if total_rows < 0:
    raise ValueError("The CSV file appears to be empty or invalid.")

rows_per_file = (total_rows + number_of_files - 1) // number_of_files

print(f"Total data rows: {total_rows:,}")
print(f"Number of files: {number_of_files}")
print(f"Maximum rows per file: {rows_per_file:,}")

with open(input_file, "r", newline="", encoding="utf-8-sig") as infile:
    reader = csv.reader(infile)
    header = next(reader, None)

    if header is None:
        raise ValueError("The CSV file is empty.")

    file_number = 1
    rows_written = 0
    outfile = None
    writer = None

    try:
        for row in reader:
            if outfile is None or rows_written >= rows_per_file:
                if outfile:
                    outfile.close()

                output_path = os.path.join(
                    output_folder,
                    f"part_{file_number}.csv"
                )

                outfile = open(
                    output_path,
                    "w",
                    newline="",
                    encoding="utf-8"
                )
                writer = csv.writer(outfile)
                writer.writerow(header)

                print(f"Creating {output_path}")
                file_number += 1
                rows_written = 0

            writer.writerow(row)
            rows_written += 1

    finally:
        if outfile:
            outfile.close()

print("\nDone! Your CSV has been split.")
print(f"Files saved in: {output_folder}/")