import re
import sys
import os
import hashlib
import logging
from datetime import datetime
from sqlite_utils import Database
from sqlite_utils.utils import rows_from_file, Format, TypeTracker


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def compute_checksum(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read and update hash in chunks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def extract_date_from_filename(filename):
    match = re.search(r'\d{4}-\d{2}-\d{2}', filename)
    return match.group(0) if match else None


def import_data(db, current_csv, table_name, checksum):
    tracker = TypeTracker()
    with open(current_csv, "rb") as f:
        rows, _ = rows_from_file(f, format=Format.CSV)
        db[table_name].insert_all(
            tracker.wrap(list(rows)),
            pk="cedula",
        )
    db[table_name].transform(types=tracker.types)
    date = (
        extract_date_from_filename(current_csv) or
        datetime.now().strftime('%Y-%m-%d')
    )
    db["imports"].insert({
        "date": date,
        "file": current_csv,
        "sha256_checksum": checksum
    })


def check_if_import_exists(db, current_checksum):
    results = db.query(
        "select count(*) from imports where sha256_checksum=?",
        [current_checksum]
    )
    count = list(results)[0].get("count(*)", 0)
    return count > 0


def create_or_update_db(current_csv):
    db_file = os.environ.get("dbfile", default="itaipu.db")
    db = Database(db_file)
    current_checksum = compute_checksum(current_csv)

    if db["imports"].exists():
        logging.info(f"Checking if {current_csv} has been imported")
        if check_if_import_exists(db, current_checksum):
            logging.info(f"Data in {current_csv} has already been imported")
            return

    nomina_table_name, _ = current_csv.split('.')
    logging.info(f"Import data from {current_csv}")
    import_data(db, current_csv, nomina_table_name, current_checksum)
    db[nomina_table_name].enable_fts(["cedula", "nombre_y_apellido"])


def main():
    filename = os.environ.get(
        "filename_template", "nomina_itaipu_{}.csv"
    )
    try:
        filename = sys.argv[1]
    except IndexError:
        filename = filename.format(datetime.now().strftime('%Y-%m-%d'))

    logging.info(f"Trying to import {filename}")

    if not os.path.exists(filename):
        logging.info(f"File {filename} not found")
        return

    create_or_update_db(filename)


if __name__ == "__main__":
    main()
