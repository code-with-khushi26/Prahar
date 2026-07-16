"""
migrate_weapons.py
Adds the new DefenseKB fact-card fields to the existing weapons table:
specs, operators, threat_classification, drdo_links.
Safe to run multiple times — skips columns that already exist.
"""

import sqlite3

conn = sqlite3.connect("database/prahar.db")
cursor = conn.cursor()

new_columns = {
    "specs": "TEXT",
    "operators": "TEXT",
    "threat_classification": "TEXT",
    "drdo_links": "TEXT",
}

cursor.execute("PRAGMA table_info(weapons)")
existing_columns = [row[1] for row in cursor.fetchall()]

for col_name, col_type in new_columns.items():
    if col_name not in existing_columns:
        cursor.execute(f"ALTER TABLE weapons ADD COLUMN {col_name} {col_type}")
        print(f"Added column: {col_name}")
    else:
        print(f"Column already exists, skipping: {col_name}")

conn.commit()
conn.close()
print("Migration complete.")