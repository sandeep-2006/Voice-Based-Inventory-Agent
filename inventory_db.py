import sqlite3

DB_NAME = "inventory.db"

# ... (ADD_ACTIONS and REMOVE_ACTIONS stay here)
ADD_ACTIONS = {
    "unloaded", "received", "arrived", "returned", "restocked", "added", "found", "got"
}

# Actions that remove from inventory
REMOVE_ACTIONS = {
    "loaded", "shipped", "sent", "dispatched",
    "delivered", "issued", "transferred", "moved", "finished", "removed", "lost", "consumed", "used", "picked"
}

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # 1. Your existing inventory table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        item TEXT PRIMARY KEY,
        quantity INTEGER,
        unit TEXT
    )
    """)

    # 2. NEW: Logs table so manager can see voice commands
    cur.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        raw_text TEXT,
        extracted_info TEXT
    )""")

    # 3. NEW: Users table for the login system
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY, 
        password TEXT, 
        role TEXT
    )""")

    # 4. NEW: Define the default roles
    cur.execute("INSERT OR IGNORE INTO users VALUES ('manager1', 'manager123', 'manager')")
    cur.execute("INSERT OR IGNORE INTO users VALUES ('worker1', 'worker123', 'worker')")

    conn.commit()
    conn.close()

# ... (rest of your update_inventory and show_inventory functions)

def log_voice_command(text, info):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("INSERT INTO logs (raw_text, extracted_info) VALUES (?, ?)", (text, info))
    conn.commit()
    conn.close()

def update_inventory(quantity, unit, item, action):
    # Validate inputs
    if not quantity or not item or not action:
        return None, None

    quantity = int(quantity)
    item = item.lower().strip()
    unit = unit.lower().strip()

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT quantity FROM inventory WHERE item = ?", (item,))
    row = cur.fetchone()

    # Decide change
    if action.lower() in ADD_ACTIONS:
        change = quantity
    elif action.lower() in REMOVE_ACTIONS:
        change = -quantity
    else:
        conn.close()
        return None, None

    if row:
        new_qty = max(0, row[0] + change)
        cur.execute(
            "UPDATE inventory SET quantity=?, unit=? WHERE item=?",
            (new_qty, unit, item)
        )
    else:
        new_qty = max(0, change)
        cur.execute(
            "INSERT INTO inventory (item, quantity, unit) VALUES (?, ?, ?)",
            (item, new_qty, unit)
        )

    conn.commit()
    conn.close()

    return item, new_qty