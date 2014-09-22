from django.core.management.base import NoArgsCommand
import hashlib
import json
import os
from django.conf import settings
from re import search


class Command(NoArgsCommand):
    help = u"""Compute hashes of static content files. Typically on deploy"""

    def handle(self, *args, **options):
        filter_ = ''
        if len(args) > 0:
            filter_ = args[0]
        self.stdout.write(json.dumps(self.get_hashes(filter_)))

    def get_hashes(self, filter_):
        hashes = {}
        module = "geography"
        static_files = self.get_static_files(module, filter_)
        for f in static_files:
            hashes['/' + f[0]] = hashlib.md5(f[1]).hexdigest()
        return hashes

    def get_static_files(self, module, filter_):
        files = []
        root = str(os.path.join(settings.PROJECT_DIR, module, 'static'))
        for path, subdirs, filenames in os.walk(root):
            for filename in filenames:
                f = os.path.join(path, filename)
                f = f.replace(root, 'static')
                f = str(f)
                if search(filter_, f):
                    files.append(f)
        return [(p, self.get_static_file_content(p, module)) for p in files]

    def get_static_file_content(self, filename, module):
        filename = os.path.join(settings.PROJECT_DIR, module, filename)
        with file(filename) as f:
            content = f.read()
        return content
