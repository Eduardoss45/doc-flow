from flask import Blueprint, request, make_response
from flask_smorest import Blueprint as ApiBlueprint, abort
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from .schemas import ClientIdResponseSchema


auth_bp = ApiBlueprint(
    "auth",
    __name__,
    url_prefix="/auth",
    description="Gerenciamento de sessão via client_id (cookie-based)",
)


@auth_bp.route("/client-id", methods=["POST"])
@auth_bp.response(200, ClientIdResponseSchema)
def generate_or_get_client_id():
    existing_client_id = request.cookies.get("client_id")

    if existing_client_id and existing_client_id.strip():
        return {
            "status": "client_id existente",
            "client_id": existing_client_id,
            "expires_at": None,
            "expires_in_seconds": 0,
        }

    client_id = str(uuid4())
    expires = datetime.now(timezone.utc) + timedelta(hours=24)

    response = make_response(
        {
            "status": "client_id gerado",
            "client_id": client_id,
            "expires_at": expires,
            "expires_in_seconds": 86400,
        }
    )

    response.set_cookie(
        key="client_id",
        value=client_id,
        max_age=24 * 3600,
        expires=expires,
        httponly=True,
        secure=request.is_secure,
        samesite="Lax",
    )

    return response
