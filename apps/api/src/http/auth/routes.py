from flask import Blueprint, request, jsonify, make_response
from uuid import uuid4
from datetime import datetime, timedelta, timezone

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/client-id", methods=["POST"])
def generate_client_id():
    existing_client_id = request.cookies.get("client_id")
    if existing_client_id and existing_client_id.strip():
        return (
            jsonify(
                {
                    "status": "client_id existente",
                    "client_id": existing_client_id,
                }
            ),
            200,
        )

    client_id = str(uuid4())

    expires = datetime.now(timezone.utc) + timedelta(hours=24)

    resp = make_response(
        jsonify(
            {
                "status": "client_id gerado",
                "client_id": client_id,
                "expires_at": expires.isoformat(),
                "expires_in_seconds": 86400,
            }
        )
    )

    resp.set_cookie(
        key="client_id",
        value=client_id,
        max_age=24 * 60 * 60,
        expires=expires,
        httponly=True,
        secure=True,
        samesite="Lax",
    )

    return resp
