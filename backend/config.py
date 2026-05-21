import os

class Config:
    MYSQL_HOST = os.getenv('DB_HOST', 'localhost')
    MYSQL_USER = os.getenv('DB_USER', 'root')
    MYSQL_PASSWORD = os.getenv('DB_PASSWORD', '')
    MYSQL_DB = os.getenv('DB_NAME', 'ecommerce_db')
    MYSQL_CURSORCLASS = 'DictCursor' # Returns rows as dictionaries instead of tuples
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'fallback-secret-key')
