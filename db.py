import os
import psycopg2
from dotenv import load_dotenv
from contextlib import contextmanager
from typing import Generator
import logging

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'user': os.getenv("user"),
    'password': os.getenv("password"),
    'host': os.getenv("host"),
    'port': os.getenv("port"),
    'dbname': os.getenv("dbname")
}

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration class."""
    
    @staticmethod
    def validate_config() -> bool:
        """Validate that all required environment variables are set."""
        required_vars = ['user', 'password', 'host', 'port', 'dbname']
        missing_vars = []
        
        for var in required_vars:
            if not DB_CONFIG[var]:
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False
        
        return True


def get_connection():
    """
    Get a database connection.
    
    Returns:
        psycopg2.connection: Database connection
        
    Raises:
        Exception: If connection fails or configuration is invalid
    """
    if not DatabaseConfig.validate_config():
        raise Exception("Invalid database configuration. Check your .env file.")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logger.debug("Database connection established")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Database connection failed: {e}")
        raise Exception(f"Failed to connect to database: {e}")


@contextmanager
def get_db_connection() -> Generator[psycopg2.extensions.connection, None, None]:
    """
    Context manager for database connections.
    Automatically handles connection cleanup.
    
    Usage:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM entries")
    """
    conn = None
    try:
        conn = get_connection()
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database operation failed: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed")


def test_connection() -> bool:
    """
    Test the database connection.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.fetchone()
        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


def initialize_database():
    """
    Initialize the database with required tables if they don't exist.
    This is useful for first-time setup.
    """
    create_tables_sql = """
    -- Enable UUID extension (if not already)
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    
    -- Table: entries
    CREATE TABLE IF NOT EXISTS entries (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        type TEXT DEFAULT 'note',
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW(),
        created_by TEXT
    );
    
    -- Table: tags
    CREATE TABLE IF NOT EXISTS tags (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        name TEXT UNIQUE NOT NULL
    );
    
    -- Table: entry_tags (many-to-many)
    CREATE TABLE IF NOT EXISTS entry_tags (
        entry_id UUID REFERENCES entries(id) ON DELETE CASCADE,
        tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
        PRIMARY KEY (entry_id, tag_id)
    );
    
    -- Create indexes for better performance
    CREATE INDEX IF NOT EXISTS idx_entries_created_at ON entries(created_at);
    CREATE INDEX IF NOT EXISTS idx_entries_type ON entries(type);
    CREATE INDEX IF NOT EXISTS idx_entries_title ON entries USING gin(to_tsvector('english', title));
    CREATE INDEX IF NOT EXISTS idx_entries_content ON entries USING gin(to_tsvector('english', content));
    """
    
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(create_tables_sql)
            conn.commit()
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False