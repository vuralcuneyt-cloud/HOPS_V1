from core.paths import get_base_path
import shutil
import sqlite3
from core.design_check import check_design_images

def run_design(progress_cb=None):
    base = get_base_path()
    main_dir = base / "1_Main"
    unmatched_dir = base / "2_Design" / "0_Portrait" / "Unmatched"
    design_root = base / "2_Design" / "0_Portrait" / "Ratio"

    files = list(main_dir.glob("*.*"))
    total = len(files)
    if total == 0:
        if progress_cb:
            progress_cb(0, 0, "⚠ 1_Main klasöründe görsel yok.")
        return

    db_path = base / "99_Logs_Reports" / "hops_v1.db"
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    design_map = {}
    nearest_map = set()
    for row in cur.execute("SELECT sku, result FROM design_pack"):
        sku, result = row
        if result.startswith("Nearest_"):
            nearest_map.add(sku)
        else:
            design_map.setdefault(sku, []).append(result)
    conn.close()

    for idx, file_path in enumerate(files, start=1):
        stem = file_path.stem
        ext = file_path.suffix
        if stem in nearest_map:
            unmatched_dir.mkdir(parents=True, exist_ok=True)
            target_path = unmatched_dir / file_path.name
            if not target_path.exists():
                shutil.move(str(file_path), str(target_path))
                msg = f"Taşındı (Nearest): {target_path.relative_to(base)}"
            else:
                msg = f"Atlandı (Zaten var): {target_path.relative_to(base)}"
        elif stem in design_map:
            for result in design_map[stem]:
                target_dir = design_root / result
                target_dir.mkdir(parents=True, exist_ok=True)
                target_path = target_dir / file_path.name
                if not target_path.exists():
                    shutil.copy2(str(file_path), str(target_path))
                    msg = f"Kopyalandı: {target_path.relative_to(base)}"
                else:
                    msg = f"Atlandı (Zaten var): {target_path.relative_to(base)}"
        else:
            msg = f"Atlandı (Design eşleşme yok): {file_path.name}"

        if progress_cb:
            percent = int((idx / total) * 100)
            progress_cb(idx, total, msg)
            
            
    if progress_cb:
        progress_cb(total, total, "Design işlemi tamamlandı. Kontrol başlatılıyor...")
    check_design_images()