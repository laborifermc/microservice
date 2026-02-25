import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import time

def create_databases():
    # Connexion à la base 'postgres' par défaut (qui existe toujours)
    # Utilise l'utilisateur que tu as défini dans docker-compose
    params = {
        "host": "db",
        "user": "db_user",
        "password": "password",
        "dbname": "postgres"
    }
    
    databases = ["product_db", "pricing_db", "inventory_db", "customer_db", "order_db"]
    
    print("[Init-DB] Waiting for PostgreSQL to be ready...")
    conn = None
    while not conn:
        try:
            conn = psycopg2.connect(**params)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        except Exception:
            time.sleep(1)

    cursor = conn.cursor()
    for db in databases:
        try:
            cursor.execute(f"CREATE DATABASE {db}")
            print(f"[Init-DB] Database '{db}' created.")
        except psycopg2.errors.DuplicateDatabase:
            print(f"[Init-DB] Database '{db}' already exists.")
        except Exception as e:
            print(f"[Init-DB] Error creating '{db}': {e}")

    cursor.close()
    conn.close()
    print("[Init-DB] All databases are ready!")

if __name__ == "__main__":
    create_databases()