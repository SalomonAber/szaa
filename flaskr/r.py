import redis
from flask import g, current_app


def get_r():
    if "r" not in g:
        g.r = redis.StrictRedis(
            host=current_app.config["CACHE_REDIS_HOST"],
            port=current_app.config["CACHE_REDIS_PORT"],
            db=current_app.config["CACHE_REDIS_DB"],
        )

    return g.r
