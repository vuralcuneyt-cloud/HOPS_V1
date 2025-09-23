from pathlib import Path
from PIL import Image
import re, datetime
from core.paths import get_base_path
from core.database import connect_db, init_db, insert_raw_data

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

def analyze_and_store_images():
    init_db()
    base = get_base_path()
    images_path = base / "0_Data"

    next_sku_number = get_next_sku()

    for img_file in images_path.glob("*.*"):
        try:
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
                original_name = img_file.stem
                created_at = datetime.datetime.now().strftime("%d/%m/%Y")

                insert_raw_data(
                    original_name,
                    sku,
                    width,
                    height,
                    ratio,
                    orientation,
                    created_at
                )

                next_sku_number += 1
        except Exception as e:
            print(f"[WARN] {img_file} işlenemedi: {e}")
