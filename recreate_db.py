import psycopg2

try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        dbname='postgres',
        user='postgres',
        password='248388',
        host='localhost'
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    # Terminate all connections to healthdb
    cur.execute("""
        SELECT pg_terminate_backend(pid)
        FROM pg_stat_activity
        WHERE datname = 'healthdb' AND pid <> pg_backend_pid()
    """)
    print("Terminated existing connections to healthdb")
    
    # Drop database if exists
    cur.execute('DROP DATABASE IF EXISTS healthdb')
    print("Dropped existing healthdb database")
    
    # Create new database
    cur.execute('CREATE DATABASE healthdb')
    print("Created new healthdb database")
    
    cur.close()
    conn.close()
    print("Database recreated successfully!")
    
except Exception as e:
    print(f"Error: {e}") 