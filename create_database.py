import pandas as pd
import sqlite3

# Correct file path
csv_file = r'static/final_customer_details.csv'  # Use raw string for the file path

try:
    # Load the CSV file into a DataFrame
    df = pd.read_csv(csv_file)

    # Proceed with database operations
    conn = sqlite3.connect('your_database.db')
    df.to_sql('customers', conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()
    print("Database created and data imported successfully!")

except OSError as e:
    print(f"Error reading the CSV file: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
