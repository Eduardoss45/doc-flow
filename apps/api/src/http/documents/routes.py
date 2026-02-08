from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from pathlib import Path
from flask import g
from src.domain.enums.conversion_type import ConversionType
from src.services.document_service import DocumentService
from src.repositories.client_storage_repository import ClientStorageRepository
from uuid import UUID

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
