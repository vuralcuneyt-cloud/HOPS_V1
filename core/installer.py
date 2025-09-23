from pathlib import Path
import sys
import os
from .paths import get_base_path

def create_directory(path: Path, hidden: bool = False):
    path.mkdir(parents=True, exist_ok=True)
    if hidden and sys.platform.startswith("win"):
        try:
            import ctypes
            FILE_ATTRIBUTE_HIDDEN = 0x02
            ctypes.windll.kernel32.SetFileAttributesW(str(path), FILE_ATTRIBUTE_HIDDEN)
        except Exception as e:
            print(f"[WARN] Gizli klasör ayarlanamadı: {e}")

def ensure_structure():
    base = get_base_path()

    folders = [
        "0_Data",
        "1_Main",
        "2_Design/0_Portrait/Ratio/Ratio_24x36/W_24",
        "2_Design/0_Portrait/Ratio/Ratio_24x36/H_36",
        "2_Design/0_Portrait/Ratio/Ratio_18x24/W_18",
        "2_Design/0_Portrait/Ratio/Ratio_18x24/H_24",
        "2_Design/0_Portrait/Ratio/Ratio_24x30/W_24",
        "2_Design/0_Portrait/Ratio/Ratio_24x30/H_30",
        "2_Design/0_Portrait/Ratio/Ratio_11x14/W_11",
        "2_Design/0_Portrait/Ratio/Ratio_11x14/H_14",
        "2_Design/0_Portrait/Ratio/Ratio_A_Series/W_23.386",
        "2_Design/0_Portrait/Ratio/Ratio_A_Series/H_33.110",
        "2_Design/0_Portrait/Unmatched",
        "2_Design/1_Landscape",
        "2_Design/2_Nearest",
        "3_Master/0_Sizes/Ratio/Ratio_24x36",
        "3_Master/0_Sizes/Ratio/Ratio_18x24",
        "3_Master/0_Sizes/Ratio/Ratio_24x30",
        "3_Master/0_Sizes/Ratio/Ratio_11x14",
        "3_Master/0_Sizes/Ratio/Ratio_A_Series",
        "3_Master/0_Sizes/Unmatched",
        "3_Master/1_Bulk",
        "4_Export/Bulk",
        "4_Export/Unmatched",
        "5_Etsy",
        "6_Etsy_Zip",
    ]

    for folder in folders:
        create_directory(base / folder)

    create_directory(base / "99_Logs_Reports", hidden=True)
    return base
