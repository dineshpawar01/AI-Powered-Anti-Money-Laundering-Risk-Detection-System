import sqlite3

def initialize_db():
    conn = sqlite3.connect('aml_database.db')
    cursor = conn.cursor()
    
    # Create the customers table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        CIF_No TEXT,
        Account_No TEXT,
        First_Name TEXT,
        Last_Name TEXT,
        Aadhaar_No TEXT,
        PAN_No TEXT,
        Date_of_Birth TEXT,
        Mobile_No TEXT,
        Address TEXT,
        flag INTEGER
    )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    initialize_db()
