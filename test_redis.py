from django_redis import get_redis_connection

try:
    r = get_redis_connection("default")
    r.set("test_key", "it_works")
    print("Redis Ping:", r.ping())  # Should print True
    print("Redis Test Key:", r.get("test_key").decode())
except Exception as e:
    print("Redis connection failed:", e)
