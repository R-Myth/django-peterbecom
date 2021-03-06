import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from peterbecom.apps.redisutils import get_redis_connection


class Command(BaseCommand):

    def handle(self, **options):
        redis = get_redis_connection()
        redis.expire('plog:hits', 1)
        redis.expire('plog:misses', 1)
        redis.expire('homepage:hits', 1)
        redis.expire('homepage:misses', 1)
        redis.set('counters-start', str(datetime.datetime.utcnow()))
