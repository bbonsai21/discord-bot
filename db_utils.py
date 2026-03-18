import sqlite3 as sql

SHOP_DB_PATH = "shop.db"

# cogs/fun.py module

# GENERAL ECONOMY
db = sql.connect(SHOP_DB_PATH)
db_cursor = db.cursor()
db_cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    balance INTEGER,
    items TEXT,
    caste TEXT,
    age INTEGER  
)
""")

db_cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    user_id INTEGER,
    item_name TEXT,
    quantity INTEGER DEFAULT 1,
    PRIMARY KEY (user_id, item_name),
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")
db.commit()
db.close()

def db_create_user(userID: int):
    conn = sql.connect(SHOP_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (id, balance, items, caste, age) VALUES (?, 0, '', 'Dalits', 18)", (userID,))
    conn.commit()
    conn.close()

def db_get_user(userID: int):
    db_create_user(userID)

    conn = sql.connect(SHOP_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT balance, items, caste, age FROM users WHERE id = ?", (userID,))
    row = cursor.fetchone()
    conn.close()
    return row

def db_add_bal(userID: int, amount: int):
    db_create_user(userID)

    conn = sql.connect(SHOP_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, userID,))
    conn.commit()
    conn.close()

def db_change_age(userID: int, age: int):
    db_create_user(userID)

    conn = sql.connect(SHOP_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET age = ? WHERE id = ?", (age, userID,))
    conn.commit()
    conn.close()

def db_add_item(user_id: int, item_name: str, amount: int = 1):
    # Add or increase an item in a user's inventory
    db_create_user(user_id)
    conn = sql.connect(SHOP_DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO inventory (user_id, item_name, quantity)
    VALUES (?, ?, ?)
    ON CONFLICT(user_id, item_name)
    DO UPDATE SET quantity = quantity + excluded.quantity
    """, (user_id, item_name, amount))

    conn.commit()
    conn.close()

def db_remove_item(user_id: int, item_name: str, amount: int = 1):
    # Decrease an item’s quantity. Deletes row if zero or less
    conn = sql.connect(SHOP_DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE inventory
    SET quantity = quantity - ?
    WHERE user_id = ? AND item_name = ?
    """, (amount, user_id, item_name))

    cursor.execute("""
    DELETE FROM inventory
    WHERE user_id = ? AND item_name = ? AND quantity <= 0
    """, (user_id, item_name))

    conn.commit()
    conn.close()

def db_get_inv(user_id: int):
    # Return list of (item_name, quantity) tuples for this user
    db_create_user(user_id)
    conn = sql.connect(SHOP_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT item_name, quantity FROM inventory WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# DAILY REWARDS
DAILY_DB_PATH = "daily.db"

db = sql.connect(DAILY_DB_PATH)
db_cursor = db.cursor()
db_cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    last_claim INTEGER
)
""")

def db_last_daily(userID: int):
    pass