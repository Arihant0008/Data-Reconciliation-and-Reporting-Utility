import pandas as pd
import os
import mysql.connector
import logging
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

logging.basicConfig(
    level = logging.INFO ,
    format= '%(asctime)s - [%(levelname)s] - %(message)s'
)

def load_local_data(filepath):
    """ Loads the local csv system output"""

    try:
        logging.info(f"Loading system data from  {filepath}")

        return pd.read_csv(filepath)
    
    except Exception as e:
        logging.error(f"failed to load csv: {e}")

        return None
    
def load_db_data(host, user, password, database):
    """Connects to MySQL and loads database table."""

    try:
        logging.info(f"Connecting to database '{database}' at {host}....")

        db_connection = mysql.connector.connect(
            host = host, 
            user = user,
            password = password,
            database = database
        )

        query = 'SELECT * FROM transactions'

        df = pd.read_sql(query, db_connection)

        db_connection.close()

        logging.info(f"Database records loaded successfully.")

        return df
    
    except Exception as err:

        logging.error(f"Database Connection failed: {err}")
        return None

def compare_datasets(sys_df, db_df):
    """Core Engine  Merges and identify discrepancies"""

    logging.info(f"Comparing datasets on 'transaction_id'...")

    merged_df = pd.merge(sys_df,db_df, on='transaction_id', how= 'outer', suffixes=('_sys','_db'), indicator=True)

    missing_in_db = merged_df[merged_df['_merge'] == 'left_only']

    phantom_in_db = merged_df[merged_df['_merge'] == 'right_only']

    both_exist = merged_df[merged_df['_merge'] == 'both']

    mismatches = both_exist[both_exist['amount_sys'] != both_exist['amount_db']]

    logging.info(f"Found {len(missing_in_db)} records missing from DB")

    logging.info(f"Found {len(phantom_in_db)} phantom records in DB.")

    logging.info(f"Found {len(mismatches)} amount mismatches")

    return missing_in_db, phantom_in_db, mismatches

def generate_report(missing, phantoms, mismatches, output_file = "discrepancy_report.csv"):
    """Concatenateserrors and exports to CSV."""

    logging.info("Generating discrepancy report...")

    final_report = pd.concat([missing,phantoms,mismatches])

    if final_report.empty:
        logging.info("Data matches perfectly. No reports needed. ")
    
    else:

        final_report.to_csv(output_file, index = False)

        logging.info(f"Report saved successfully as '{output_file}'")

# --- MAIN EXECUTION ---

def main():
    logging.info("--- RECONCILIATION UTILITY STARTED ---")

    sys_df = load_local_data('system_records.csv')

    db_df = load_db_data(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)

    if sys_df is not None and db_df is not None:

        missing, phantoms, mismatches = compare_datasets(sys_df, db_df)

        generate_report(missing, phantoms, mismatches)
    
    else:
        logging.error("Reconciliation aborted due to data ingestion failure.")

    logging.info("--- RECONCILIATION UTILITY FINISHED")

if __name__ == "__main__":
    main()