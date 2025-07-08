from rest_framework.throttling import BaseThrottle
from django.core.cache import caches
import time

class TimeIntervalThrottle(BaseThrottle):
    def __init__(self):
        self.cache_key_prefix = 'throttle_'
        self.max_requests = 5 
        self.reset_time = 72 * 3600
        self.cache = caches['default']

    def get_cache_key(self, request):
        if request.user :
            return f"{self.cache_key_prefix}{request.user.userid}"
        else:
            return f"{self.cache_key_prefix}{request.META['REMOTE_ADDR']}"

    def allow_request(self, request, view):
        now = time.time()
        cache_key = self.get_cache_key(request)
        request_count = self.cache.get(cache_key, default=0)
        if request_count >= self.max_requests:
            return False
        
        request_count += 1
        self.cache.set(cache_key, request_count, self.reset_time)
        return True

    def wait(self):
        return self.reset_time
