import sqlite3
import json

conn = sqlite3.connect("database/prahar.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS weapons (
        id INTEGER PRIMARY KEY,
        name TEXT,
        type TEXT,
        country TEXT,
        description TEXT
    )
""")

# Load JSON
with open("data/prahar_kb.json") as f:
    weapons = json.load(f)

# Insert each weapon
for w in weapons:
    cursor.execute("""
        INSERT OR IGNORE INTO weapons (id, name, type, country, description)
        VALUES (?, ?, ?, ?, ?)
    """, (w["id"], w["name"], w["type"], w["country"], w["description"]))

conn.commit()
conn.close()

print(f"Done! {len(weapons)} weapons inserted.")