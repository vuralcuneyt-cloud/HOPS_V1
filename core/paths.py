from pathlib import Path

def get_base_path() -> Path:
    """
    Platforma uygun kullanıcı dizininde HOPS_V1 ana klasörünü döndürür.
    Windows: C:/Users/<username>/HOPS_V1
    Linux/Mac: /home/<username>/HOPS_V1
    """
    return Path.home() / "HOPS_V1"
