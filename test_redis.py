from app.core.redis import redis_client

redis_client.set("test_key", "hello_natraj")
print(redis_client.get("test_key"))
