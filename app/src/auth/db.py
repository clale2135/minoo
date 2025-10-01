import os
import bcrypt
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime

# Cloud SQL connection configuration
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT', 5432)
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    """Initialize database tables"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username VARCHAR(255) PRIMARY KEY,
                    password VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE,
                    auth_type VARCHAR(50) DEFAULT 'standard',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS user_preferences (
                    username VARCHAR(255) PRIMARY KEY REFERENCES users(username),
                    color_preferences JSONB,
                    style_preferences JSONB
                );
                
                CREATE TABLE IF NOT EXISTS outfits (
                    id UUID PRIMARY KEY,
                    username VARCHAR(255) REFERENCES users(username),
                    name VARCHAR(255),
                    items JSONB,
                    occasion VARCHAR(255),
                    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        conn.commit() 