import logging
import redis
from config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_USER

logger = logging.getLogger(__name__)

try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        username=REDIS_USER,
        decode_responses=True,
    )
    # Test the connection so a failure doesn't stop app startup
    redis_client.ping()
except redis.RedisError as exc:
    logger.warning("Redis connection failed: %s", exc)
    redis_client = None
