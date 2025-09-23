from pathlib import Path
from typing import Callable, Optional
from core.paths import get_base_path
from core.database import connect_db


def _fetch_sku_by_original_name(original_name: str) -> Optional[str]:
    conn = connect_db()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT sku FROM raw_data WHERE original_name = ? LIMIT 1",
            (original_name,),
        )
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def _fetch_orientation_by_sku(sku: str) -> Optional[str]:
    conn = connect_db()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT orientation FROM raw_data WHERE sku = ? LIMIT 1",
            (sku,),
        )
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def _is_nearest_for_sku(sku: str) -> bool:
    conn = connect_db()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT result FROM design_pack WHERE sku = ?",
            (sku,),
        )
        rows = cur.fetchall()
        for (result,) in rows:
            if isinstance(result, str) and result.startswith("Nearest_"):
                return True
        return False
    finally:
        conn.close()


def perform_split_up(progress_cb: Optional[Callable[[int, int, str], None]] = None):
    base = get_base_path()
    data_dir = base / "0_Data"
    dest_landscape = base / "2_Design" / "1_Landscape"
    dest_nearest = base / "2_Design" / "2_Nearest"
    dest_main = base / "1_Main"

    files = list(data_dir.glob("*.*"))
    total = len(files)

    for idx, file_path in enumerate(files, start=1):
        try:
            stem = file_path.stem
            ext = file_path.suffix

            sku = _fetch_sku_by_original_name(stem)
            if not sku:
                if progress_cb:
                    progress_cb(idx, total, f"Atlandı (SKU bulunamadı): {file_path.name}")
                continue

            # 1) Adı SKU ile değiştir (aynıysa geç)
            desired_name = f"{sku}{ext}"
            desired_path = file_path.with_name(desired_name)
            if desired_path != file_path:
                # Var ise üzerine yazmak için önce mevcutu sil (kopya yaratmadan)
                if desired_path.exists():
                    desired_path.unlink()
                file_path.rename(desired_path)
                file_path = desired_path

            # 2) Yerine göre taşı
            orientation = _fetch_orientation_by_sku(sku)
            if orientation in ("horizontal", "square"):
                target_dir = dest_landscape
            else:
                # vertical/square kabul
                if _is_nearest_for_sku(sku):
                    target_dir = dest_nearest
                else:
                    target_dir = dest_main

            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = target_dir / file_path.name
            if target_path.exists():
                target_path.unlink()
            file_path.replace(target_path)

            if progress_cb:
                progress_cb(idx, total, f"Taşındı: {target_path.relative_to(base)}")
        except Exception as e:
            if progress_cb:
                progress_cb(idx, total, f"[WARN] İşlenemedi: {file_path.name} -> {e}")
            else:
                print(f"[WARN] İşlenemedi: {file_path} -> {e}")


