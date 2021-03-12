""" 
CRU parser
"""

__author__ = "Robert Berry"
__version__ = "0.1.0"
__license__ = "MIT"

import argparse
import re
import sys
import sqlite3
import itertools

from logzero import logger


def create_db(db_file):
    # Add table to database and create it if it doesn't exist
    try:
        db = sqlite3.connect(db_file)
        cursor = db.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS rainfall 
                          (xRef INT, yRef INT, Date TEXT, Value INT);""")
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_file_years(cru_file):
    with open(args.cru_file) as f:
        for line in f:
            # Do a regex to find the years 
            match = re.search("Years=(\d+)-(\d+)", line)
            # Once we've matched, get data and break
            if match:
                start_year, end_year = int(match.group(1)), int(match.group(2))
                break
    return start_year, end_year


def main(db_file, cru_file):
    # Find the number of years to process
    start_year, end_year = get_file_years(cru_file)
    number_of_years = end_year - start_year + 1

    # Create the db and table
    create_db(db_file)

    # Do the work
    # Open DB here rather than doing it multiple times
    logger.info(f"Loading {number_of_years} years ({start_year}-{end_year}) of data into {db_file} database")
    db = sqlite3.connect(db_file)
    cursor = db.cursor()

    # Set some counters used in the loop
    year_counter = 0
    cell_counter = 0
    value_counter = 0
    commit_counter = 0

    with open(cru_file) as f:
        for line in itertools.islice(f, 5, None):
            # Determine if we are starting a new block
            match = re.search("Grid-ref=\s+(\d+),\s+(\d+)", line)
            if match:
                # Get the xref and yref if starting block
                xref, yref = int(match.group(1)), int(match.group(2))
                cell_counter += 1
                year_counter = 0
            else:
                # Generate a date list for current line
                line_year = start_year + year_counter
                date = [f"{1}/{x}/{line_year}" for x in range(1, 13)]
                # Regex out the data 
                data = [int(x) for x in re.findall('.....', line)]
                # Check we have 12 values
                if len(data) != 12:
                    logger.error(f"Incorrect number of values for {xref}, {yref}")
                    sys.exit(0)
                # Combine the xref, yref, date and data
                insert_data = zip(itertools.repeat(xref), itertools.repeat(yref), date, data)
                cursor.executemany("""INSERT INTO rainfall (xRef, yRef, Date, Value)
                                      VALUES (?, ?, ?, ?)""", insert_data)
                year_counter += 1
                value_counter += 12
                commit_counter += 12

            # Only commit periodically to save time
            if commit_counter >= 100000:
                db.commit()
                commit_counter = 0

    # Do a final commit to catch anything missing from the counter
    db.commit()
    db.close()
    logger.info("Processed {} grid cells, containing {} rainfall readings".format(cell_counter, value_counter))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f'{__doc__.strip()} (version {__version__})', add_help=False)

    required = parser.add_argument_group('Required named arguments')
    required.add_argument('-c', '--cru_file', help='CRU input file', required=True)
    required.add_argument('-d', '--db_file', help='SQLite database file', required=True)

    optional = parser.add_argument_group('optional arguments')
    optional.add_argument('-h', '--help', action='help', help='Show this help message and exit')

    args = parser.parse_args()
    main(args.db_file, args.cru_file)
