"""
WSGI config for geography project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
import sys
DIRNAME = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(DIRNAME)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geography.settings")

from django.core.wsgi import get_wsgi_application

def application(environ, start_response):
    # pass the WSGI environment variables on through to os.environ
    for k, v in environ.iteritems():
        if isinstance(k, str) and (k.startswith('GEOGRAPHY') or k.startswith('PROSO')):
            os.environ[k] = v
    return get_wsgi_application()(environ, start_response)
