from pathlib import Path
from typing import Callable, Optional, Dict, List
import sqlite3
from core.paths import get_base_path


def _list_expected_master_codes() -> Dict[str, List[str]]:
    """
    Returns mapping: { sku: [master_frame_code, ...] } for non-Nearest results.
    """
    base = get_base_path()
    db_path = base / "99_Logs_Reports" / "hops_v1.db"
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    rows = cur.execute(
        """
        SELECT sku, master_frame_code
        FROM design_pack
        WHERE result NOT LIKE 'Nearest_%' AND master_frame_code IS NOT NULL AND master_frame_code <> ''
        """
    ).fetchall()
    conn.close()

    sku_to_codes: Dict[str, List[str]] = {}
    for sku, code in rows:
        sku_to_codes.setdefault(sku, []).append(code)
    return sku_to_codes


def _has_any_with_stem(folder: Path, stem: str) -> bool:
    if not folder.exists():
        return False
    for p in folder.iterdir():
        if p.is_file() and p.stem == stem:
            return True
    return False


def run_design_process_check(progress_cb: Optional[Callable[[int, int, str], None]] = None) -> Path:
    """
    Checks 5_Etsy/<SKU>/ for presence of expected master files based on design_pack (non-Nearest).
    Writes missing items to 99_Logs_Reports/missing_files.txt.
    If 6_Etsy_Zip/<SKU>.zip exists, that SKU is skipped (not reported as missing).
    Returns path to the report file.
    """
    base = get_base_path()
    etsy_root = base / "5_Etsy"
    zip_root = base / "6_Etsy_Zip"
    report_path = base / "99_Logs_Reports" / "missing_files.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    sku_to_codes = _list_expected_master_codes()
    items = list(sku_to_codes.items())
    total = len(items)

    missing_lines: List[str] = []

    for idx, (sku, codes) in enumerate(items, start=1):
        try:
            # Skip if zip already exists
            zip_file = zip_root / f"{sku}.zip"
            if zip_file.exists():
                if progress_cb:
                    progress_cb(idx, total, f"Atlandı (zip var): {zip_file.name}")
                continue

            sku_dir = etsy_root / sku
            for code in codes:
                exists = _has_any_with_stem(sku_dir, code)
                if not exists:
                    missing_lines.append(f"{sku}\t{code}")

            if progress_cb:
                progress_cb(idx, total, f"Kontrol edildi: {sku}")
        except Exception as e:
            if progress_cb:
                progress_cb(idx, total, f"Hata: {sku} -> {e}")

    # Write report
    if missing_lines:
        report_path.write_text("\n".join(missing_lines), encoding="utf-8")
    else:
        # Create/overwrite empty report
        report_path.write_text("", encoding="utf-8")

    return report_path



