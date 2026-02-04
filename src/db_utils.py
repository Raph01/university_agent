import sqlite3
import os

# Get the absolute path to the database
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "university.db"))

def get_db_connection(read_only=True):
    """
    Returns a connection to the SQLite database.
    If read_only is True, it prevents any modifications (INSERT, UPDATE, DELETE).
    """
    try:
        if read_only:
            # The 'mode=ro' tells SQLite to open the file in Read-Only mode
            conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        else:
            conn = sqlite3.connect(DB_PATH)
        
        # This allows us to access columns by name (e.g., row['first_name'])
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def run_query(query, params=()):
    """
    Safely executes a read-only query and returns all results.
    """
    conn = get_db_connection(read_only=True)
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        # Convert sqlite3.Row objects to standard dictionaries for the AI
        return [dict(row) for row in results]
    except sqlite3.Error as e:
        return [{"error": str(e)}]
    finally:
        conn.close()
