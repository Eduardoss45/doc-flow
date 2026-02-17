from flask_socketio import SocketIO
from app.config import config

socketio = SocketIO(
    cors_allowed_origins=config.ALLOWED_ORIGINS or "*",
    manage_session=False,
    async_mode="threading",
    logger=True,
    engineio_logger=True,
)
