from core.paths import get_base_path
from PIL import Image
import sqlite3
from datetime import datetime
from pathlib import Path

def get_master_design(image_name, width, height):
    sku = image_name.split('-')[0].split('.')[0]  # HOPS_10000188
    # 1. width veya height 5400/7200 ise
    if width == 5400 or height == 7200:
        return f"{sku}_R18x24_300DPI_sRGB"
    # 2. width veya height 3300/4200 ise
    if width == 3300 or height == 4200:
        return f"{sku}_R11x14_300DPI_sRGB"
    # 3. width veya height 7017/9933 ise
    if width == 7017 or height == 9933:
        return f"{sku}_RA1_300DPI_sRGB"
    # 4. height 10800 ise
    if height == 10800:
        return f"{sku}_R24x36_300DPI_sRGB"
    # 5. height 9000 ise
    if height == 9000:
        return f"{sku}_R24x30_300DPI_sRGB"
    # 6. width 7200 ise
    if width == 7200:
        if height >= 10800:
            return f"{sku}_R24x36_300DPI_sRGB"
        elif 9000 <= height < 10800:
            return f"{sku}_R24x30_300DPI_sRGB"
    return ""


def run_master_bulk_check(progress_cb=None):
    base = get_base_path()
    bulk_dir = base / "3_Master" / "1_Bulk"
    db_path = base / "99_Logs_Reports" / "hops_v1.db"
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

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

    files = list(bulk_dir.glob("*.*"))
    total = len(files)
    for idx, file_path in enumerate(files, start=1):
        try:
            with Image.open(file_path) as img:
                width, height = img.size
            # Kaydı uzantısız dosya adı ile tut
            image_name_no_ext = file_path.stem
            master_design = get_master_design(image_name_no_ext, width, height)
            cur.execute(
                "INSERT OR REPLACE INTO master_check (image_name, width, height, master_design, checked_at) VALUES (?, ?, ?, ?, ?)",
                (image_name_no_ext, width, height, master_design, datetime.now().isoformat())
            )
            msg = f"{file_path.name} kaydedildi."
        except Exception as e:
            msg = f"{file_path.name} hata: {e}"
        if progress_cb:
            progress_cb(idx, total, msg)

    conn.commit()
    conn.close()


def _dest_ratio_folder(master_code: str) -> Path | None:
    """
    master_code: e.g. HOPS_10000187_R24x30_300DPI_sRGB
    Returns destination subfolder under 3_Master/0_Sizes/Ratio
    """
    base = get_base_path()
    ratio_root = base / "3_Master" / "0_Sizes" / "Ratio"
    try:
        code = master_code.split('_')[2]  # R24x30, RA1, R18x24
    except Exception:
        return None

    if code == "RA1":
        return ratio_root / "Ratio_A_Series"
    # For codes like R24x36, R24x30, R18x24, R11x14
    if code.startswith('R'):
        return ratio_root / f"Ratio_{code[1:]}"
    return None


def perform_master_moves(progress_cb=None):
    """
    3_Master/1_Bulk içindeki dosyaları master_check tablosuna göre
    uygun Ratio alt klasörlerine taşır ve dosya adını master_design olarak değiştirir.
    """
    base = get_base_path()
    bulk_dir = base / "3_Master" / "1_Bulk"

    db_path = base / "99_Logs_Reports" / "hops_v1.db"
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("SELECT image_name, master_design FROM master_check WHERE master_design IS NOT NULL AND master_design <> ''")
    rows = cur.fetchall()
    conn.close()

    total = len(rows)
    for idx, (image_name_no_ext, master_design) in enumerate(rows, start=1):
        try:
            # Bul bulk kaynak dosya (herhangi bir uzantı)
            candidates = list(bulk_dir.glob(f"{image_name_no_ext}.*"))
            if not candidates:
                if progress_cb:
                    progress_cb(idx, total, f"Atlandı (kaynak yok): {image_name_no_ext}")
                continue
            src = candidates[0]

            dest_ratio = _dest_ratio_folder(master_design)
            if dest_ratio is None:
                if progress_cb:
                    progress_cb(idx, total, f"Atlandı (hedef oran bulunamadı): {image_name_no_ext}")
                continue

            dest_ratio.mkdir(parents=True, exist_ok=True)
            new_name = f"{master_design}{src.suffix}"
            dest_path = dest_ratio / new_name

            if dest_path.exists():
                dest_path.unlink()

            src.replace(dest_path)
            if progress_cb:
                progress_cb(idx, total, f"Taşındı: {dest_path.relative_to(base)}")
        except Exception as e:
            if progress_cb:
                progress_cb(idx, total, f"Hata: {image_name_no_ext} -> {e}")
            else:
                print(f"[WARN] {image_name_no_ext} taşınamadı: {e}")