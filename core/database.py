import sqlite3
from pathlib import Path
from .paths import get_base_path

DB_NAME = "hops_v1.db"

def get_db_path() -> Path:
    return get_base_path() / "99_Logs_Reports" / DB_NAME

def connect_db():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    return conn

def init_db():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS raw_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_name TEXT NOT NULL,
        sku TEXT NOT NULL,
        width INTEGER,
        height INTEGER,
        ratio REAL,
        orientation TEXT,
        created_at TEXT
    )
    """)

    # design_pack tablosu
    cur.execute("""
    CREATE TABLE IF NOT EXISTS design_pack (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT NOT NULL,
        result TEXT,
        master_frame_code TEXT
    )
    """)

    conn.commit()
    conn.close()


def insert_raw_data(original_name, sku, width, height, ratio, orientation, created_at):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO raw_data (original_name, sku, width, height, ratio, orientation, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (original_name, sku, width, height, ratio, orientation, created_at))
    conn.commit()
    conn.close()

def insert_design_pack(sku, result, master_frame_code=None):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO design_pack (sku, result, master_frame_code)
        VALUES (?, ?, ?)
    """, (sku, result, master_frame_code))
    conn.commit()
    conn.close()

def fetch_all_raw_data(limit=100):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM raw_data ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows
