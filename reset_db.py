import sqlite3

DB_NAME = "inventory.db"

def reset_database():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Clear inventory table
    cur.execute("DELETE FROM inventory")
    
    # Clear logs table
    cur.execute("DELETE FROM logs")
    
    # Optional: reset autoincrement for logs
    cur.execute("DELETE FROM sqlite_sequence WHERE name='logs'")

    conn.commit()
    conn.close()
    print("Inventory and logs have been cleared!")

if __name__ == "__main__":
    reset_database()