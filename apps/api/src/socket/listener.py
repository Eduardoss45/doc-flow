import time
import json
from src.infra.redis.client import get_redis_client
from src.infra.redis.redis_pub import NOTIFICATION_CHANNEL


def start_redis_listener():
    from src.socket.server import socketio
