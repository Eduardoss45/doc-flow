from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from pathlib import Path
from flask import g
from src.domain.enums.conversion_type import ConversionType
from src.services.document_service import DocumentService

documents_bp = Blueprint("documents", __name__, url_prefix="/documents")

ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls", "txt", "pdf", "docx", "doc"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@documents_bp.route("/upload", methods=["POST"])
def upload_and_convert():
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

    input_dir = Path("src/infrastructure/storage/input")
    input_dir.mkdir(parents=True, exist_ok=True)

    original_name = secure_filename(file.filename)

    service: DocumentService = g.document_service

    job = service.create_job(
        conversion_type=conversion_type,
        input_path="",
        input_filename=original_name,
    )

    input_path = input_dir / f"{job.id}_{original_name}"
    job.input_path = str(input_path)

    service.repository.update(job)

    file.save(input_path)

    from src.workers.conversion_worker import process_conversion

    process_conversion.delay(str(job.id))

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
