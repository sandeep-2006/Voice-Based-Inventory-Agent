import sqlite3

DB_NAME = "inventory.db"

# STOCK IN (adds to inventory)
ADD_ACTIONS = {
    "unloaded", "received", "arrived", "returned", "restocked"
}

# STOCK OUT (removes from inventory)
REMOVE_ACTIONS = {
    "loaded", "shipped", "sent", "dispatched",
    "delivered", "issued", "transferred", "moved","finished"
}


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        item TEXT PRIMARY KEY,
        quantity INTEGER,
        unit TEXT
    )
    """)

    conn.commit()
    conn.close()


def update_inventory(quantity, unit, item, action):

    if item is None or quantity is None:
        print("Invalid data — skipping database update")
        return

    quantity = int(quantity)

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Check existing quantity
    cur.execute("SELECT quantity FROM inventory WHERE item = ?", (item,))
    row = cur.fetchone()

    # Decide add or subtract
    if action in ADD_ACTIONS:
        change = quantity          # STOCK IN
    elif action in REMOVE_ACTIONS:
        change = -quantity         # STOCK OUT
    else:
        print("Unknown action — no change made")
        conn.close()
        return

    if row:
        new_qty = row[0] + change

        # Prevent negative inventory
        if new_qty < 0:
            new_qty = 0

        cur.execute("""
            UPDATE inventory
            SET quantity = ?, unit = ?
            WHERE item = ?
        """, (new_qty, unit, item))

        print(f"{item} updated → {new_qty} {unit}")

    else:
        # If item not present, insert with initial qty
        initial_qty = max(0, change)

        cur.execute("""
            INSERT INTO inventory (item, quantity, unit)
            VALUES (?, ?, ?)
        """, (item, initial_qty, unit))

        print(f"{item} inserted → {initial_qty} {unit}")

    conn.commit()
    conn.close()

def show_inventory():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT item, quantity, unit FROM inventory")

    rows = cur.fetchall()

    print("\n📦 Current Inventory in Database:")
    print("----------------------------------")

    if not rows:
        print("Inventory is empty")
    else:
        for item, qty, unit in rows:
            print(f"{item} → {qty} {unit}")

    conn.close()