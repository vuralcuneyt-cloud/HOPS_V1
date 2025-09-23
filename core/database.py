import sqlite3
from pathlib import Path
from .paths import get_base_path

DB_NAME = "hops_v1.db"

def get_db_path() -> Path:
    return get_base_path() / "99_Logs_Reports" / DB_NAME

def connect_db():
    db_path = get_db_path()
    # Fail fast if locked to avoid freezing the UI
    conn = sqlite3.connect(db_path, timeout=1, check_same_thread=False)
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA busy_timeout=1000")
    except Exception:
        pass
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

    # design_check tablosu (sku+result benzersiz)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS design_check (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT,
        result TEXT,
        file_exists INTEGER,
        checked_at TEXT,
        UNIQUE(sku, result)
    )
    """)

    # master_check tablosu (image_name benzersiz)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS master_check (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        image_name TEXT UNIQUE,
        width INTEGER,
        height INTEGER,
        master_design TEXT,
        checked_at TEXT
    )
    """)

    # Mevcut duplikatları temizle (raw_data: aynı original_name için en son kaydı tut)
    try:
        cur.execute(
            """
            WITH keep AS (
                SELECT MAX(id) AS id FROM raw_data GROUP BY original_name
            )
            DELETE FROM raw_data
            WHERE id NOT IN (SELECT id FROM keep)
            """
        )
    except Exception:
        # Eski SQLite sürümlerinde CTE desteklenmiyorsa sessiz geç
        pass

    # Benzersizlik: original_name için unique index (tekrarlı kayıtları önlemek için)
    cur.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS idx_raw_data_original_name
    ON raw_data(original_name)
    """)

    # design_pack duplikatlarını temizle (aynı sku, result, master_frame_code için en son kaydı tut)
    try:
        cur.execute(
            """
            WITH keep AS (
                SELECT MAX(id) AS id
                FROM design_pack
                GROUP BY sku, result, master_frame_code
            )
            DELETE FROM design_pack
            WHERE id NOT IN (SELECT id FROM keep)
            """
        )
    except Exception:
        pass

    # Nearest tekrarlarını da engellemek için master_frame_code NULL/'' normalize et
    try:
        cur.execute("UPDATE design_pack SET master_frame_code = '' WHERE master_frame_code IS NULL")
    except Exception:
        pass

    # Benzersizlik: sku+result düzeyinde unique index (master_frame_code yoksa tekrar oluşmasın)
    cur.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS idx_design_pack_unique_sr
    ON design_pack(sku, result)
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
    try:
        cur.execute(
            """
            INSERT INTO design_pack (sku, result, master_frame_code)
            VALUES (?, ?, ?)
            ON CONFLICT(sku, result) DO NOTHING
            """,
            (sku, result, master_frame_code),
        )
    except sqlite3.IntegrityError:
        # Son çare: sessizce yoksay
        pass
    conn.commit()
    conn.close()

def fetch_all_raw_data(limit=100):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM raw_data ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows


def original_name_exists(original_name: str) -> bool:
    conn = connect_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM raw_data WHERE original_name = ? LIMIT 1", (original_name,))
        return cur.fetchone() is not None
    finally:
        conn.close()


def get_raw_data_count() -> int:
    conn = connect_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(1) FROM raw_data")
        row = cur.fetchone()
        return int(row[0]) if row else 0
    finally:
        conn.close()


def reset_db():
    """
    Tüm tablo verilerini temizler ve AUTOINCREMENT sayaçlarını sıfırlar.
    """
    conn = connect_db()
    cur = conn.cursor()
    try:
        def table_exists(name: str) -> bool:
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
            return cur.fetchone() is not None

        target_tables = [
            'raw_data',
            'design_pack',
            'design_check',  # opsiyonel, yoksa atlanır
            'master_check',  # opsiyonel, yoksa atlanır
        ]

        for t in target_tables:
            if table_exists(t):
                try:
                    cur.execute(f"DELETE FROM {t}")
                except Exception:
                    pass

        # AUTOINCREMENT sayaçlarını sıfırla (sqlite_sequence mevcutsa)
        try:
            existing = [t for t in target_tables if table_exists(t)]
            if existing:
                in_list = ",".join([f"'{t}'" for t in existing])
                cur.execute(f"DELETE FROM sqlite_sequence WHERE name IN ({in_list})")
        except Exception:
            pass

        conn.commit()
    finally:
        conn.close()
