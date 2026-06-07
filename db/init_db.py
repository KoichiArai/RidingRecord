import sqlite3

DB_NAME = "RidingRecords.db"

conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS records (
    numberOfSaddle INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT DEFAULT CURRENT_TIMESTAMP
    className TEXT NOT NULL
    time TEXT DEFAULT CURRENT_TIMESTAMP
    instructorName TEXT NOT NULL
    horseName TEXT NOT NULL
    horseMemo TEXT NOT NULL
    body TEXT NOT NULL    
);
""")

conn.commit()
conn.close()
print("DB initialized.")