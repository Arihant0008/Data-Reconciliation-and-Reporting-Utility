import pandas as pd
import mysql.connector

def run_reconciliation():
    print("Starting Data Reconciliation...")

    # --- 1. INGEST DATA ---
    # We use Pandas to read the CSV files and turn them into DataFrames (like virtual Excel tables).
    sys_df = pd.read_csv('system_records.csv')
    # db_df = pd.read_csv('db_records.csv')

    print("Connecting to MySQL Database...")
    try:

        db_connection = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "Arihant123",
            database = "reconciliation_db"
        )

        query = "SELECT * FROM transactions"

        db_df = pd.read_sql(query, db_connection)

    except mysql.connector.Error as err:
        print(f"[ERROR] Database connection failed: {err}")
        return # Stop the script if the DB is down
        


    # --- 2. COMPARE DATA (THE CORE ENGINE) ---
    # We merge the two tables together using 'transaction_id' as our common key.
    # 'how=outer' means we keep every record from both files. Nothing gets left behind.
    # 'suffixes' renames columns with the same name (like 'amount') so we know which came from where.
    # 'indicator=True' is the magic trick: it adds a column called '_merge' telling us exactly where the row came from!

    merged_df = pd.merge(sys_df,db_df,on='transaction_id',how='outer', suffixes=('_sys', '_db'), indicator=True)



    # Error A: Missing in DB (System says it happened, DB doesn't have it)
    # The '_merge' column will say 'left_only' because it only exists in the left file (system_records)

    missing_in_db = merged_df[merged_df['_merge'] == 'left_only']
    print(f"\n[ALERT] Found {len(missing_in_db)} records missing from the database.")


    # Error B: Phantom in DB (DB has it, but System never sent it)
    # The '_merge' column will say 'right_only'
    phantom_in_db = merged_df[merged_df['_merge'] == 'right_only']
    print(f"[ALERT] Found {len(phantom_in_db)} phantom records in the database.")



    # Error C: Mismatched Amounts (Exists in both, but the numbers don't match)
    # First, filter to records that exist in 'both'
    both_exist = merged_df[merged_df['_merge'] == 'both']

    # Then, check where the system amount does NOT equal the database amount
    mismatches = both_exist[both_exist['amount_sys'] != both_exist['amount_db']]
    print(f"[ALERT] Found {len(mismatches)} records with mismatched amounts.")


    # --- 4. GENERATE REPORT ---
    # We combine all our error tables into one master discrepancy report
    
    final_report = pd.concat([missing_in_db, phantom_in_db, mismatches])

    # We export this final report back to a CSV file so the Ops team can review it
    final_report.to_csv('discrepancy_report.csv', index=False)
    print("\n[SUCCESS] Reconciliation complete. Report saved as 'discrepancy_report.csv'.")

    if db_connection.is_connected():
        db_connection.close()

# This tells Python to run the function when we execute the script
if __name__ == "__main__":
    run_reconciliation()