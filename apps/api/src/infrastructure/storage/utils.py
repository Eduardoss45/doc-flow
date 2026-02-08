from pathlib import Path
from uuid import UUID


def get_client_input_dir(client_id: str | UUID) -> Path:
    cid = str(client_id)
    return Path("src/infrastructure/storage/input") / cid


def get_client_output_dir(client_id: str | UUID) -> Path:
    cid = str(client_id)
    return Path("src/infrastructure/storage/output") / cid


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
