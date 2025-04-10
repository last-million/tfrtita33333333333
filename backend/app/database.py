"""
This module initializes the MySQL database connection using mysql.connector
and provides a function to create necessary tables.
"""
import mysql.connector
from mysql.connector import pooling
from mysql.connector import Error
from .config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db_pool = None

def init_db_pool():
    """Initializes the database connection pool."""
    global db_pool
    try:
        logger.info(f"Attempting to connect to MySQL: Host={settings.db_host}, User={settings.db_user}, DB={settings.db_name}")
        db_pool = pooling.MySQLConnectionPool(
            pool_name="tfrtita_pool",
            pool_size=5, # Adjust pool size as needed
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name
        )
        logger.info("MySQL connection pool created successfully.")
        # Test connection
        conn = db_pool.get_connection()
        if conn.is_connected():
            logger.info("Successfully connected to MySQL database.")
            conn.close()
        else:
            logger.error("Failed to establish initial connection from pool.")
            db_pool = None # Reset pool if initial connection failed

    except Error as e:
        logger.error(f"Error while connecting to MySQL using Connection Pool: {e}")
        db_pool = None # Ensure pool is None if initialization fails

def get_db_connection():
    """Gets a connection from the pool."""
    if db_pool is None:
        logger.error("Database pool is not initialized.")
        return None
    try:
        conn = db_pool.get_connection()
        if conn.is_connected():
            return conn
    except Error as e:
        logger.error(f"Error getting connection from pool: {e}")
    return None

def create_tables():
    """
    Create the necessary tables in the MySQL database.
    Adjusts syntax for MySQL (e.g., TEXT type, AUTO_INCREMENT if needed).
    """
    conn = get_db_connection()
    if conn is None:
        logger.error("Cannot create tables: No database connection.")
        return

    cursor = None
    try:
        cursor = conn.cursor()
        logger.info("Creating table: call_logs")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS call_logs (
                call_sid VARCHAR(255) PRIMARY KEY,
                from_number VARCHAR(50),
                to_number VARCHAR(50),
                direction VARCHAR(20),
                status VARCHAR(50),
                start_time DATETIME,
                end_time DATETIME,
                duration INTEGER,
                recording_url TEXT,
                transcription LONGTEXT
            );
            """
        )
        logger.info("Creating table: knowledge_base")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS knowledge_base (
                document_id VARCHAR(255) PRIMARY KEY,
                title TEXT,
                source TEXT,
                mime_type VARCHAR(100),
                size INTEGER,
                last_modified DATETIME,
                vector BLOB  -- Consider LONGBLOB if vectors are large
            );
            """
        )
        conn.commit()
        logger.info("Tables checked/created successfully.")
    except Error as e:
        logger.error(f"Error creating tables: {e}")
        # Consider rolling back if part of a larger transaction
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Initialize the pool when the module is loaded
init_db_pool()

# Allow running this script directly to create tables (e.g., during deployment)
if __name__ == "__main__":
    if db_pool:
        create_tables()
    else:
        logger.error("Database pool initialization failed. Cannot create tables.")
