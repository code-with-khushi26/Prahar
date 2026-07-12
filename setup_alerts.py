import sqlite3

conn = sqlite3.connect("database/prahar.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        module TEXT NOT NULL,
        severity TEXT NOT NULL,
        raw_result TEXT NOT NULL,
        enriched_context TEXT
    )
""")
conn.commit()
conn.close()
print("alerts table created successfully")