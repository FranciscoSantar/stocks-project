import psycopg
import os

def create_connection():
    try:
        conn = psycopg.connect(
            dbname=os.environ.get('PGDATABASE'),
            user=os.environ.get('PGUSER'),
            password=os.environ.get('PGPASSWORD'),
            host=os.environ.get('PGHOST')
        )
        return conn
    except Exception as e:
        print(e)
        return False

def get_cursor(connection):
    if connection:
        return connection.cursor()
    else:
        return False

def close_cursor_and_coonection(connection, cursor):
        cursor.close()
        connection.close()
        return True