# -*- encoding: utf-8 -*-
from django.core.cache import cache
from geography.models.user import is_lazy


def cache_per_user(ttl=None, prefix=None):
    def decorator(function):
        def apply_cache(request, *args, **kwargs):
            user = request.user.id if not is_lazy(request.user) else 'lazy'
            CACHE_KEY = 'view_cache_%s_%s_%s' % (
                function.__name__, request.LANGUAGE_CODE, user)
            response = cache.get(CACHE_KEY, None)
            if not response:
                response = function(request, *args, **kwargs)
                cache.set(CACHE_KEY, response, ttl)
            return response
        return apply_cache
    return decorator
