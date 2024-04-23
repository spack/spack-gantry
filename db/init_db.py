import os
import sqlite3
import sys

# Usage: python init_db.py <db_path>
# loads in default tables and future schema changes into the database
db_path = sys.argv[1]

# check if the database exists as a file
if os.path.isfile(db_path):
    print(f"database {db_path} already exists")
    sys.exit(0)

try:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    with open("schema.sql", "r") as f:
        c.executescript(f.read())
    conn.commit()
    conn.close()
except sqlite3.Error as e:
    print(e)
    sys.exit(1)

print(f"database initialized successfully to {db_path}")
