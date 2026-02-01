from flask import Blueprint, request, jsonify, current_app

from src.domain.enums.conversion_type import ConversionType

documents_bp = Blueprint("documents", __name__, url_prefix="/documents")


@documents_bp.route("", methods=["POST"])
def create_document():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    try:
        conversion_type = ConversionType(data["conversion_type"])
        input_path = data["input_path"]
    except (KeyError, ValueError):
        return jsonify({"error": "Invalid payload"}), 400

    service = current_app.extensions["document_service"]

    job = service.create_job(conversion_type=conversion_type, input_path=input_path)

    return (
        jsonify(
            {
                "id": str(job.id),
                "status": job.status.value,
                "conversion_type": job.conversion_type.value,
            }
        ),
        200,
    )
