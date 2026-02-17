import time
import json
from infra.redis.client import get_redis_client
from infra.redis.redis_pub import NOTIFICATION_CHANNEL


def start_redis_listener():
    from app.realtime.server import socketio
