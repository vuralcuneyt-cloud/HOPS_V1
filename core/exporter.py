from pathlib import Path
from typing import Callable, Optional
from core.paths import get_base_path


def _extract_sku(filename: str) -> str:
    # Expect names like HOPS_10000190_R24x30_300DPI_sRGB.jpg or .pdf
    name = Path(filename).stem
    # Take part before first underscore after HOPS prefix
    # e.g., HOPS_10000190_R24x30... -> HOPS_10000190
    parts = name.split("_")
    if len(parts) >= 2:
        return f"{parts[0]}_{parts[1]}"
    return parts[0]


def perform_export(progress_cb: Optional[Callable[[int, int, str], None]] = None):
    base = get_base_path()
    src_dir = base / "4_Export" / "Bulk"
    dest_root = base / "5_Etsy"
    dest_root.mkdir(parents=True, exist_ok=True)

    # Include images and PDFs
    files = [p for p in src_dir.glob("*.*") if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".pdf"}]
    total = len(files)

    for idx, file_path in enumerate(files, start=1):
        try:
            sku = _extract_sku(file_path.name)
            if not sku:
                if progress_cb:
                    progress_cb(idx, total, f"Atlandı (SKU çözülemedi): {file_path.name}")
                continue

            target_dir = dest_root / sku
            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = target_dir / file_path.name

            if target_path.exists():
                target_path.unlink()

            file_path.replace(target_path)

            if progress_cb:
                progress_cb(idx, total, f"Taşındı: {target_path.relative_to(base)}")
        except Exception as e:
            if progress_cb:
                progress_cb(idx, total, f"Hata: {file_path.name} -> {e}")
            else:
                print(f"[WARN] {file_path} taşınamadı: {e}")


