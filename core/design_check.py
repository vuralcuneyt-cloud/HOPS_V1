from core.paths import get_base_path
import sqlite3
from datetime import datetime

def check_design_images():
    base = get_base_path()
    design_root = base / "2_Design" / "0_Portrait" / "Ratio"
    db_path = base / "99_Logs_Reports" / "hops_v1.db"
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    # Tabloyu oluştur (sku+result benzersiz)
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

    # Sadece Nearest_ olmayan satırları al
    rows = cur.execute("SELECT sku, result FROM design_pack WHERE result NOT LIKE 'Nearest_%'").fetchall()

    # Her satırı işle
    for sku, result in rows:
        target_dir = design_root / result
        found = False
        for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff']:
            file_path = target_dir / f"{sku}{ext}"
            if file_path.exists():
                found = True
                break
        cur.execute(
            "INSERT OR REPLACE INTO design_check (sku, result, file_exists, checked_at) VALUES (?, ?, ?, ?)",
            (sku, result, int(found), datetime.now().isoformat())
        )

    conn.commit()
    conn.close()
