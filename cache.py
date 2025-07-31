import redis
from config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_USER

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    username=REDIS_USER,
    decode_responses=True,
)
