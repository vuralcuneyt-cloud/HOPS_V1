from pathlib import Path
from typing import Callable, Optional
import shutil
from core.paths import get_base_path


def perform_etsy_zip(progress_cb: Optional[Callable[[int, int, str], None]] = None):
    base = get_base_path()
    etsy_root = base / "5_Etsy"
    zip_root = base / "6_Etsy_Zip"
    zip_root.mkdir(parents=True, exist_ok=True)

    folders = [p for p in etsy_root.iterdir() if p.is_dir()]
    total = len(folders)

    for idx, folder in enumerate(folders, start=1):
        try:
            zip_base = zip_root / folder.name
            zip_path = Path(str(zip_base) + ".zip")
            if zip_path.exists():
                zip_path.unlink()
            # shutil.make_archive expects base_name without extension
            shutil.make_archive(str(zip_base), 'zip', root_dir=str(folder))
            if progress_cb:
                progress_cb(idx, total, f"Zip oluşturuldu: {zip_path.name}")
        except Exception as e:
            if progress_cb:
                progress_cb(idx, total, f"Hata: {folder.name} -> {e}")
            else:
                print(f"[WARN] Zip oluşturulamadı: {folder} -> {e}")


