
import os
import psycopg

database_url = "postgresql://spam_toxic_db_user:Uz1iWznUs00CeNCYAU8rtKRp8KNwu5hT@dpg-db495rm0tbcc73djie50-a.singapore-postgres.render.com/spam_toxic_db"

if not database_url:
    raise RuntimeError("DATABASE_URL is not set.")

try:
    with psycopg.connect(
        database_url,
        connect_timeout=10,
        sslmode="require"
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            print("PostgreSQL connection successful!")
            print(cursor.fetchone()[0])

except Exception as error:
    print("Connection failed:", error)
