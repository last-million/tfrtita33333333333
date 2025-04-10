"""
This module initializes the LibSQL database connection and provides a function to
create necessary tables. It first attempts to use the synchronous client from libsql_client;
if that fails, it falls back to a simple SQLite-based implementation.
"""

from .config import settings

# Try to import and instantiate the LibSQL synchronous client.
try:
    from libsql_client.sync import Client as SyncClient
    # Instantiate without arguments as indicated by the error message
    # It likely reads connection info from environment variables (DATABASE_URL)
    db = SyncClient()
    # Optionally, add a check or execute a simple query to confirm connection
    db.execute("SELECT 1")
    print("Connected to LibSQL database using SyncClient")
except Exception as e:
    print(f"Error connecting to LibSQL database using SyncClient: {e}")
    print("Falling back to a concrete SQLite implementation (in-memory).")
    
    # Fallback: use sqlite3 as a concrete client implementation.
    import sqlite3

    class ConcreteClient:
        def __init__(self, url):
            # For demonstration, we ignore the URL and use an in-memory SQLite database.
            self.conn = sqlite3.connect(":memory:")
            self.closed = False

        def execute(self, query):
            cur = self.conn.cursor()
            cur.execute(query)
            self.conn.commit()

        def transaction(self):
            # Return self as a context manager.
            return self

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            # No special exit handling.
            pass

        def batch(self, queries):
            cur = self.conn.cursor()
            for query in queries:
                cur.execute(query)
            self.conn.commit()

        def close(self):
            self.conn.close()
            self.closed = True

    db = ConcreteClient(url=settings.database_url)
    print("Connected to fallback SQLite in-memory database.")


def create_tables():
    """
    Create the necessary tables in the database.
    """
    if db is None:
        print("Database connection is not available.")
        return

    try:
        with db.transaction() as tx:
            tx.execute(
                """
                CREATE TABLE IF NOT EXISTS call_logs (
                    call_sid TEXT PRIMARY KEY,
                    from_number TEXT,
                    to_number TEXT,
                    direction TEXT,
                    status TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    duration INTEGER,
                    recording_url TEXT,
                    transcription TEXT
                );
                """
            )
            tx.execute(
                """
                CREATE TABLE IF NOT EXISTS knowledge_base (
                    document_id TEXT PRIMARY KEY,
                    title TEXT,
                    source TEXT,
                    mime_type TEXT,
                    size INTEGER,
                    last_modified TEXT,
                    vector BLOB
                );
                """
            )
            print("Tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")


if __name__ == "__main__":
    create_tables()
