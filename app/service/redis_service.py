import json
import redis
import appdb
from flask import current_app


class RedisService:
    _instance = None
    _redis_client = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = RedisService()
        return cls._instance

    def __init__(self):
        self._redis_client = None

    def connect(self):
        """Establish connection to Redis server"""
        if self._redis_client is None:
            try:
                self._redis_client = redis.from_url(appdb.REDIS_URL)
                self._redis_client.ping()  # Test connection
                current_app.logger.info("Connected to Redis successfully")
            except redis.RedisError as e:
                current_app.logger.error(f"Failed to connect to Redis: {str(e)}")
                print(f"Failed to connect to Redis: {str(e)}")
                self._redis_client = None
        return self._redis_client

    def is_connected(self):
        """Check if Redis is connected and available"""
        if not self._redis_client:
            return False
        try:
            self._redis_client.ping()
            return True
        except redis.RedisError:
            return False

    def get(self, key):
        """Get data from Redis"""
        if not self.is_connected():
            return None
        try:
            data = self._redis_client.get(key)
            return json.loads(data) if data else None
        except (redis.RedisError, json.JSONDecodeError) as e:
            current_app.logger.error(f"Redis get error: {str(e)}")
            return None

    def set(self, key, value, expiration=None):
        """Store data in Redis with optional expiration"""
        if not self.is_connected():
            return False

        try:
            if expiration is None:
                expiration = current_app.config.get('REDIS_EXPIRATION', 86400)

            self._redis_client.setex(
                key,
                expiration,
                json.dumps(value)
            )
            return True
        except redis.RedisError as e:
            current_app.logger.error(f"Redis set error: {str(e)}")
            return False

    def delete(self, key):
        """Remove data from Redis"""
        if not self.is_connected():
            return False

        try:
            self._redis_client.delete(key)
            return True
        except redis.RedisError as e:
            current_app.logger.error(f"Redis delete error: {str(e)}")
            return False

    def get_sorted_range(self, key, start, count):
        """Get a range of items from a sorted list"""
        if not self.is_connected():
            return []
        try:
            data = self.get(key)
            if not data or not isinstance(data, list):
                return []
            return data[start:start + count]
        except Exception as e:
            current_app.logger.error(f"Redis get_sorted_range error: {str(e)}")
            return []

    def set_list(self, key, values, expiration=None):
        """Store a list in Redis"""
        return self.set(key, values, expiration)

    def add_to_sorted_set(self, key, value, score, expiration=None):
        """Add a value to a sorted set with given score"""
        if not self.is_connected():
            return False
        try:
            self._redis_client.zadd(key, {str(value): score})
            if expiration:
                self._redis_client.expire(key, expiration)
            return True
        except redis.RedisError as e:
            current_app.logger.error(f"Redis sorted set error: {str(e)}")
            return False

    def get_from_sorted_set(self, key, start=0, end=-1, desc=True):
        """Get range of values from sorted set"""
        if not self.is_connected():
            return []
        try:
            if desc:
                return self._redis_client.zrevrange(key, start, end)
            else:
                return self._redis_client.zrange(key, start, end)
        except redis.RedisError as e:
            current_app.logger.error(f"Redis sorted set get error: {str(e)}")
            return []

    def get_sorted_set_length(self, key):
        """Get the length of a sorted set"""
        if not self.is_connected():
            return 0
        try:
            return self._redis_client.zcard(key)
        except redis.RedisError as e:
            current_app.logger.error(f"Redis sorted set length error: {str(e)}")
            return 0

    def hset(self, key, field, value):
        """Set a field in a Redis hash"""
        if not self.is_connected():
            return False
        try:
            # Convert value to string if needed
            if isinstance(value, (bool, int, float)):
                value = str(value)
            elif value is None:
                value = ""

            self._redis_client.hset(key, field, value)
            return True
        except redis.RedisError as e:
            current_app.logger.error(f"Redis hset error: {str(e)}")
            return False
