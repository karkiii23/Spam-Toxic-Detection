
import os
import sqlite3
import psycopg

SQLITE_PATH = "database/users.db"
DATABASE_URL = "postgresql://spam_toxic_db_user:Uz1iWznUs00CeNCYAU8rtKRp8KNwu5hT@dpg-db495rm0tbcc73djie50-a.singapore-postgres.render.com/spam_toxic_db"
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set.")

if not os.path.exists(SQLITE_PATH):
    raise FileNotFoundError(SQLITE_PATH)

# Read SQLite data
with sqlite3.connect(SQLITE_PATH) as sqlite_conn:
    sqlite_conn.row_factory = sqlite3.Row

    users = [
        dict(row)
        for row in sqlite_conn.execute("SELECT * FROM users")
    ]

    history = [
        dict(row)
        for row in sqlite_conn.execute(
            "SELECT * FROM analysis_history"
        )
    ]

print("Users found:", len(users))
print("History records found:", len(history))

# Verify that the expected columns exist
required_users = {"id", "username", "email", "password"}
required_history = {
    "id", "user_id", "message", "spam_result",
    "toxic_result", "overall_result", "analysis_type",
    "created_at"
}

if users and not required_users.issubset(users[0]):
    raise ValueError("Your SQLite users schema differs from the expected schema.")

if history and not required_history.issubset(history[0]):
    raise ValueError("Your SQLite history schema differs from the expected schema.")

# Insert records into PostgreSQL
with psycopg.connect(DATABASE_URL, sslmode="require") as conn:
    with conn.cursor() as cur:
        # Refuse to merge into non-empty tables accidentally
        cur.execute("SELECT COUNT(*) FROM users")
        pg_users = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM analysis_history")
        pg_history = cur.fetchone()[0]

        if pg_users or pg_history:
            raise RuntimeError(
                "PostgreSQL tables are not empty. "
                "Stop and verify the existing records before migrating."
            )

        for row in users:
            cur.execute(
                """
                INSERT INTO users (id, username, email, password)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    row["id"], row["username"],
                    row["email"], row["password"]
                )
            )

        for row in history:
            cur.execute(
                """
                INSERT INTO analysis_history (
                    id, user_id, message, spam_result,
                    toxic_result, overall_result,
                    analysis_type, created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    row["id"], row["user_id"], row["message"],
                    row["spam_result"], row["toxic_result"],
                    row["overall_result"], row["analysis_type"],
                    row["created_at"]
                )
            )

        # Ensure future IDs continue after the migrated records
        cur.execute("""
            SELECT setval(
                pg_get_serial_sequence('users', 'id'),
                COALESCE((SELECT MAX(id) FROM users), 1),
                EXISTS (SELECT 1 FROM users)
            )
        """)

        cur.execute("""
            SELECT setval(
                pg_get_serial_sequence('analysis_history', 'id'),
                COALESCE((SELECT MAX(id) FROM analysis_history), 1),
                EXISTS (SELECT 1 FROM analysis_history)
            )
        """)

    conn.commit()

print("Migration completed successfully.")
