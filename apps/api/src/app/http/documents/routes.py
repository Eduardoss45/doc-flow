from flask import (
    Blueprint,
    request,
    jsonify,
    send_from_directory,
    current_app,
    g,
)
from flask_smorest import Blueprint as ApiBlueprint, abort
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from pathlib import Path
from uuid import UUID
from datetime import datetime, timezone
from .schemas import UploadFormSchema, JobCreatedSchema, FileListSchema, FileItemSchema
from app.infra.utils import get_client_output_dir, get_client_input_dir
from app.domain.enums.conversion_type import ConversionType
from app.services.document_service import DocumentService


documents_bp = ApiBlueprint(
    "documents",
    __name__,
    url_prefix="/documents",
    description="Upload, conversão, listagem e download de documentos",
)


ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls", "txt", "pdf", "docx", "doc"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@documents_bp.route("/upload", methods=["POST"])
@documents_bp.arguments(UploadFormSchema, location="form")
@documents_bp.response(202, JobCreatedSchema)
def upload_and_convert(conversion_data):
    conversion_type = ConversionType(conversion_data["conversion_type"])

    client_id_str = request.cookies.get("client_id")
    if not client_id_str or not client_id_str.strip():
        abort(400, messages={"cookie": "client_id cookie is required"})

    try:
        client_id = UUID(client_id_str)
    except ValueError:
        abort(400, messages={"cookie": "client_id inválido"})

    if "file" not in request.files:
        abort(400, messages={"file": "Nenhum arquivo enviado"})

    file: FileStorage = request.files["file"]
    if not file or not file.filename:
        abort(400, messages={"file": "Nome de arquivo inválido"})

    if not allowed_file(file.filename):
        abort(400, messages={"file": "Formato de arquivo não suportado"})

    storage_repo = g.storage_repository
    storage = storage_repo.get_or_create(client_id)

    approx_size = file.content_length or len(file.read())
    file.seek(0)

    can_upload, reason = storage.can_upload(approx_size)
    if not can_upload:
        abort(403, messages={"upload": reason})

    service: DocumentService = g.document_service

    job = service.create_job(
        client_id=client_id,
        conversion_type=conversion_type,
        input_filename=secure_filename(file.filename),
    )

    file.save(job.input_path)
    service.job_repo.update(job)

    from app.workers.tasks.conversion_worker import process_conversion

    process_conversion.delay(str(job.id), str(client_id))

    return {
        "job_id": str(job.id),
        "status": job.status.value,
        "message": "Upload recebido. Processamento enfileirado.",
    }, 202


@documents_bp.route("/files", methods=["GET"])
@documents_bp.route("/history", methods=["GET"])
@documents_bp.response(200, FileListSchema)
def list_user_files():
    client_id_str = request.cookies.get("client_id")
    if not client_id_str or not client_id_str.strip():
        abort(400, messages={"cookie": "client_id cookie is required"})

    try:
        client_id = UUID(client_id_str)
    except ValueError:
        abort(400, messages={"cookie": "client_id inválido"})

    storage_repo = g.storage_repository

    storage = storage_repo.get_by_client_id(client_id)

    output_dir: Path = get_client_output_dir(client_id)
    files_list = []

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
                    "download_url": download_url,
                    "extension": entry.suffix.lstrip(".").upper() or None,
                }
            )

    return {
        "client_id": str(client_id),
        "count": len(files_list),
        "files": files_list,
        "has_more": False,
    }, 200


@documents_bp.route(
    "/download/output/<uuid:client_id>/<path:filename>", methods=["GET"]
)
def download_converted_file(client_id: UUID, filename: str):
    cookie_client_id = request.cookies.get("client_id")
    if not cookie_client_id or cookie_client_id != str(client_id):
        abort(403, messages={"auth": "Acesso negado: client_id não corresponde"})

    output_dir: Path = get_client_output_dir(client_id)
    safe_filename = secure_filename(filename)
    file_path = output_dir / safe_filename

    if not file_path.is_file():
        current_app.logger.error(f"Arquivo não encontrado: {file_path}")
        abort(404, messages={"file": "Arquivo não encontrado ou já expirado/deletado"})

    return send_from_directory(
        str(output_dir),
        safe_filename,
        as_attachment=True,
        download_name=filename,
        max_age=0,
    )
