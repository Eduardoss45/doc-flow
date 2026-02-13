from flask import (
    Blueprint,
    request,
    jsonify,
    send_from_directory,
    abort,
    current_app,
    g,
)
from infrastructure.storage.utils import get_client_output_dir, get_client_input_dir
from src.repositories.client_storage_repository import ClientStorageRepository
from src.domain.enums.conversion_type import ConversionType
from src.services.document_service import DocumentService
from werkzeug.utils import secure_filename
from typing import List, Dict
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID
import os


documents_bp = Blueprint("documents", __name__, url_prefix="/documents")

ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls", "txt", "pdf", "docx", "doc"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@documents_bp.route("/upload", methods=["POST"])
def upload_and_convert():
    client_id_str = request.cookies.get("client_id")
    if not client_id_str or client_id_str.strip() == "":
        return jsonify({"error": "client_id cookie is required"}), 400
    try:
        client_id = UUID(client_id_str)
    except ValueError:
        return jsonify({"error": "client_id inválido"}), 400

    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = request.files["file"]

    if not file or file.filename == "":
        return jsonify({"error": "Nome de arquivo inválido"}), 400

    conversion_str = request.form.get("conversion_type")
    if not conversion_str:
        return jsonify({"error": "conversion_type obrigatório"}), 400

    try:
        conversion_type = ConversionType(conversion_str)
    except ValueError:
        return jsonify({"error": f"conversion_type inválido: {conversion_str}"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Formato de arquivo não suportado"}), 400

    storage_repo = ClientStorageRepository(g.db)
    storage = storage_repo.get_or_create(client_id)

    input_dir = Path("src/infrastructure/storage/input")

    approx_size = file.content_length or 0
    if approx_size == 0:
        file_content = file.read()
        approx_size = len(file_content)
        file.seek(0)
    else:
        file_content = None

    can, reason = storage.can_upload(approx_size)
    if not can:
        return jsonify({"error": reason}), 403

    service: DocumentService = g.document_service

    job = service.create_job(
        client_id=client_id,
        conversion_type=conversion_type,
        input_filename=secure_filename(file.filename),
    )

    file.save(job.input_path)

    service.job_repo.update(job)

    from src.workers.conversion_worker import process_conversion

    process_conversion.delay(str(job.id), str(client_id))

    return (
        jsonify(
            {
                "job_id": str(job.id),
                "status": job.status.value,
                "message": "Upload recebido. Processamento enfileirado.",
            }
        ),
        202,
    )


@documents_bp.route("/files", methods=["GET"])
@documents_bp.route("/history", methods=["GET"])
def list_user_files():
    client_id_str = request.cookies.get("client_id")
    if not client_id_str or not client_id_str.strip():
        return jsonify({"error": "client_id cookie is required"}), 400

    try:
        client_id = UUID(client_id_str)
    except ValueError:
        return jsonify({"error": "client_id inválido"}), 400

    storage_repo = ClientStorageRepository(g.db)
    storage = storage_repo.get_by_client_id(client_id)
    if not storage:
        return jsonify({"error": "Cliente não encontrado"}), 404

    output_dir: Path = get_client_output_dir(client_id)

    files_list: List[Dict] = []

    if output_dir.is_dir():
        for entry in output_dir.iterdir():
            if not entry.is_file():
                continue

            try:
                stat = entry.stat()
            except OSError:
                continue

            filename = entry.name
            download_url = f"{request.host_url.rstrip('/')}/documents/download/output/{client_id}/{filename}"

            files_list.append(
                {
                    "filename": filename,
                    "size_bytes": stat.st_size,
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "modified_at": datetime.fromtimestamp(
                        stat.st_mtime, tz=timezone.utc
                    ).isoformat(),
                    "download_url": download_url,
                    "extension": entry.suffix.lstrip(".").upper() or None,
                }
            )

    files_list.sort(key=lambda x: x["modified_at"], reverse=True)

    return jsonify(
        {
            "client_id": str(client_id),
            "count": len(files_list),
            "files": files_list,
            "has_more": False,
        }
    )


@documents_bp.route(
    "/download/output/<uuid:client_id>/<path:filename>", methods=["GET"]
)
def download_converted_file(client_id: UUID, filename: str):
    cookie_client_id = request.cookies.get("client_id")
    if not cookie_client_id or cookie_client_id != str(client_id):
        abort(403, "Acesso negado: client_id não corresponde")

    output_dir: Path = get_client_output_dir(client_id)

    current_app.logger.info(f"Download solicitado: client={client_id}, file={filename}")
    current_app.logger.info(f"Output dir: {output_dir} (existe? {output_dir.exists()})")
    if output_dir.exists():
        files = [f.name for f in output_dir.iterdir() if f.is_file()]
        current_app.logger.info(f"Arquivos no diretório: {files}")

    safe_filename = secure_filename(filename)
    file_path = output_dir / safe_filename

    if not file_path.is_file():
        current_app.logger.error(f"Arquivo não encontrado: {file_path}")
        abort(404, "Arquivo não encontrado ou já expirado/deletado")

    return send_from_directory(
        str(output_dir),
        safe_filename,
        as_attachment=True,
        download_name=filename,
        max_age=0,
    )
