from pathlib import Path
from PIL import Image
import re, datetime
from core.paths import get_base_path
from core.database import connect_db, init_db, insert_raw_data, original_name_exists

def get_next_sku():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT sku FROM raw_data ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    if row:
        match = re.match(r"HOPS_(\d+)", row[0])
        if match:
            return int(match.group(1)) + 1
    return 10000001

def analyze_and_store_images(files: list[Path] | None = None, progress_cb=None):
    """
    Verilen dosya listesi üzerinde analiz yapar ve DB'ye ekler.
    Aynı original_name var ise resmi siler ve atlar.

    progress_cb: optional callable(index:int, total:int, message:str)
    """
    init_db()
    base = get_base_path()
    images_path = base / "0_Data"

    if files is None:
        files = list(images_path.glob("*.*"))

    total = len(files)
    next_sku_number = get_next_sku()

    for idx, img_file in enumerate(files, start=1):
        try:
            original_name = img_file.stem

            # Duplicate guard: varsa geç (dosyayı silme)
            if original_name_exists(original_name):
                if progress_cb:
                    progress_cb(idx, total, f"Atlandı (duplikat): {original_name}")
                continue

            with Image.open(img_file) as img:
                width, height = img.size
                ratio = round(width / height, 2)

            if width > height:
                orientation = "horizontal"
            elif height > width:
                orientation = "vertical"
            else:
                orientation = "square"

            sku = f"HOPS_{next_sku_number:08d}"
            created_at = datetime.datetime.now().strftime("%d/%m/%Y")

            insert_raw_data(
                original_name,
                sku,
                width,
                height,
                ratio,
                orientation,
                created_at,
            )

            next_sku_number += 1

            # Başarılı ilerleme bildirimi
            if progress_cb:
                progress_cb(idx, total, f"{idx}/{total} görsel işlendi...")
        except Exception as e:
            if progress_cb:
                progress_cb(idx, total, f"[WARN] {img_file.name} işlenemedi: {e}")
            else:
                print(f"[WARN] {img_file} işlenemedi: {e}")
