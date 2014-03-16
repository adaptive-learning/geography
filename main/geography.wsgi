import os
import sys
from django.core.handlers.wsgi import WSGIHandler

DIRNAME = os.path.abspath(os.path.dirname(__file__))
sys.path.append(DIRNAME)


class WSGIEnvironment(WSGIHandler):
    def __call__(self, environ, start_response):
        for k, v in environ.iteritems():
            if isinstance(k, str) and k.startswith('GEOGRAPHY'):
                os.environ[k] = v
        os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
        return super(WSGIEnvironment, self).__call__(environ, start_response)


application = WSGIEnvironment()



