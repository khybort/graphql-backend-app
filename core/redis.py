import redis


class Redis:
    _redis = redis.Redis(host="redis", port=6379, db=0)

    @classmethod
    def send_message(cls, channel: str, message: str):
        cls._redis.publish(channel, message)

    @classmethod
    def subscribe(cls, channel: str):
        p = cls._redis.pubsub()
        p.subscribe(channel)
        return p

    @staticmethod
    def get_message(p):
        message = p.get_message()
        if message and message["type"] == "message":
            return message["data"].decode("utf-8")
        return None

    @classmethod
    def get(cls, key):
        value = cls._redis.get(key)
        return value and value.decode("utf-8")

    @classmethod
    def get_raw(cls, key):
        return cls._redis.get(key)

    @classmethod
    def set(cls, key, value, exp=None):
        cls._redis.set(key, value, ex=exp)

    @classmethod
    def exists(cls, key):
        return cls._redis.exists(key)

    @classmethod
    def delete(cls, key):
        cls._redis.delete(key)
