from django.conf import settings
from django.db import connection
from social_auth.exceptions import AuthAlreadyAssociated
from django.contrib.auth import logout
from django.shortcuts import redirect


class SqldumpMiddleware(object):

    def process_response(self, request, response):
        if settings.DEBUG and 'sqldump' in request.GET:
            response.content = str(connection.queries)
            response['Content-Type'] = 'text/plain'
        return response


class AuthAlreadyAssociatedMiddleware(object):

    def process_exception(self, request, exception):
        if isinstance(exception, AuthAlreadyAssociated):
            url = request.path  # should be something like '/complete/google/'
            url = url.replace("complete", "login")
            logout(request)
            return redirect(url)
