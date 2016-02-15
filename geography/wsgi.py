import os
import sys
DIRNAME = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(DIRNAME)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geography.settings")

from django.core.wsgi import get_wsgi_application


def application(environ, start_response):
    # pass the WSGI environment variables on through to os.environ
    for k, v in environ.items():
        if isinstance(k, str) and (k.startswith('GEOGRAPHY') or k.startswith('PROSO')):
            os.environ[k] = v
    return get_wsgi_application()(environ, start_response)
