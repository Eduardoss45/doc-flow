from pathlib import Path
from uuid import UUID


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def get_client_input_dir(client_id: str | UUID) -> Path:
    cid = str(client_id)
    dir_path = PROJECT_ROOT / "src" / "app" / "infra" / "storage" / "input" / cid
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_client_output_dir(client_id: str | UUID) -> Path:
    cid = str(client_id)
    dir_path = PROJECT_ROOT / "src" / "app" / "infra" / "storage" / "output" / cid
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_directory_size(directory: Path) -> int:
    """Calcula tamanho total em bytes de todos os arquivos na pasta (recursivo)"""
    if not directory.exists() or not directory.is_dir():
        return 0
    total = 0
    for file_path in directory.rglob("*"):
        if file_path.is_file() and not file_path.is_symlink():
            try:
                total += file_path.stat().st_size
            except (PermissionError, FileNotFoundError):
                pass
    return total
