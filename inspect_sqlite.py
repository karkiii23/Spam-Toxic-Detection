
import sqlite3
from pathlib import Path

db_path = Path("database/users.db")

if not db_path.exists():
    print("Database not found:", db_path.resolve())
    print("Check your project for the actual .db file.")
    raise SystemExit(1)

connection = sqlite3.connect(db_path)
cursor = connection.cursor()

cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
      AND name NOT LIKE 'sqlite_%'
""")

tables = cursor.fetchall()

print("Database:", db_path.resolve())
print("\nTables found:")

for (table_name,) in tables:
    print(f"\n--- {table_name} ---")

    cursor.execute(f'PRAGMA table_info("{table_name}")')

    for column in cursor.fetchall():
        print("Column:", column[1], "| Type:", column[2])

    cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
    print("Rows:", cursor.fetchone()[0])

connection.close()
