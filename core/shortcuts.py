import sys
import os
from pathlib import Path
from .paths import get_base_path

def create_folder_shortcut():
    """Masaüstüne HOPS_V1 klasörü için kısayol oluşturur."""
    base = get_base_path()
    desktop = Path.home() / "Desktop"
    shortcut_path = desktop / "HOPS_V1_Folder.lnk"

    if sys.platform.startswith("win"):
        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortcut(str(shortcut_path))
            shortcut.TargetPath = str(base)
            shortcut.WorkingDirectory = str(base)
            shortcut.IconLocation = "explorer.exe,0"
            shortcut.save()
            print(f"[OK] Klasör kısayolu oluşturuldu: {shortcut_path}")
        except Exception as e:
            print(f"[WARN] Klasör kısayolu oluşturulamadı: {e}")
    else:
        # Linux/Mac için sembolik link
        if not shortcut_path.exists():
            os.symlink(base, shortcut_path)

def create_exe_shortcut():
    """Masaüstüne HOPS_V1.exe kısayolu oluşturur."""
    desktop = Path.home() / "Desktop"
    shortcut_path = desktop / "HOPS_V1.lnk"

    # EXE dosyasının yolu (PyInstaller çıkışı)
    exe_path = Path(__file__).resolve().parent.parent / "dist" / "HOPS_V1.exe"
    # Icon yolu (varsa kullan)
    icon_path = Path(__file__).resolve().parent.parent / "assets" / "hop.ico"

    if sys.platform.startswith("win"):
        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortcut(str(shortcut_path))
            shortcut.TargetPath = str(exe_path)
            shortcut.WorkingDirectory = str(exe_path.parent)
            shortcut.IconLocation = str(icon_path) if icon_path.exists() else str(exe_path)
            shortcut.save()
            print(f"[OK] Exe kısayolu oluşturuldu: {shortcut_path}")
        except Exception as e:
            print(f"[WARN] Exe kısayolu oluşturulamadı: {e}")
    else:
        shortcut_file = desktop / "HOPS_V1.desktop"
        content = f"""[Desktop Entry]
Type=Application
Name=HOPS_V1
Exec={exe_path}
Icon=utilities-terminal
Terminal=false
"""
        shortcut_file.write_text(content)
        shortcut_file.chmod(0o755)
        print(f"[OK] Exe kısayolu oluşturuldu: {shortcut_file}")

def create_all_shortcuts():
    """Hem klasör hem exe kısayollarını oluşturur (birbirini silmez)."""
    create_folder_shortcut()
    create_exe_shortcut()

create_shortcuts = create_all_shortcuts
