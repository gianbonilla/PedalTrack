import hashlib

def hash_password(p): return hashlib.sha256(p.encode()).hexdigest()

def seed_database(db):
    if db.conn.execute("SELECT COUNT(*) FROM staff").fetchone()[0] > 0:
        return
    db.conn.executemany("INSERT OR IGNORE INTO staff(username,password_hash,first_name,last_name,role,contact_number) VALUES(?,?,?,?,?,?)", [
        ("admin",    hash_password("admin1234"),  "System", "Admin",   "admin",    "0000-000-0000"),
        ("analim",   hash_password("cashier123"), "Ana",    "Lim",     "cashier",  "0917-555-1001"),
        ("rpascual", hash_password("mech123"),    "Ramon",  "Pascual", "mechanic", "0928-555-2002"),
    ])
    db.conn.executemany("INSERT INTO customer(first_name,last_name,contact_number,email) VALUES(?,?,?,?)", [
        ("Maria","Santos","0917-123-4567","m.santos@email.com"),
        ("Ben","Reyes","0928-555-9012","b.reyes@email.com"),
        ("Lara","Tan","0905-777-3344","lara.tan@email.com"),
        ("Rico","Cruz","0932-400-8821",None),
    ])
    db.conn.executemany("INSERT INTO bike(bike_code,brand,model,size,color) VALUES(?,?,?,?,?)", [
        ("BK-001","Trek","Marlin 5","small","Red"),
        ("BK-002","Trek","Marlin 5","medium","Blue"),
        ("BK-003","Polygon","Cascade","small","Green"),
        ("BK-004","Polygon","Cascade","medium","Black"),
        ("BK-005","Giant","Talon 3","large","White"),
        ("BK-006","Giant","Talon 3","large","Gray"),
        ("BK-007","Raleigh","Talus 2","medium","Orange"),
        ("BK-008","Raleigh","Talus 2","small","Yellow"),
    ])
    db.conn.commit()
