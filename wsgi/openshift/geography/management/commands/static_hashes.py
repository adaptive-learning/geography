from django.core.management.base import NoArgsCommand
import hashlib
import json
import os
from django.conf import settings


class Command(NoArgsCommand):
    help = u"""Compute hashes of static content files. Typically on deploy"""

    def handle_noargs(self, **options):
        self.stdout.write(json.dumps(self.get_hashes()))

    def get_hashes(self):
        hashes = {}
        module = "core"
        static_files = self.get_static_files(module)
        for f in static_files:
            hashes[f[0]] = hashlib.md5(f[1]).hexdigest()
        return hashes

    def get_static_files(self, module):
        files = []
        root = str(os.path.join(settings.PROJECT_DIR, module, 'static'))
        for path, subdirs, filenames in os.walk(root):
            for filename in filenames:
                f = os.path.join(path, filename)
                f = f.replace(root, 'static')
                files.append(str(f))
        return [(p, self.get_static_file_content(p, module)) for p in files]

    def get_static_file_content(self, filename, module):
        filename = os.path.join(settings.PROJECT_DIR, module, filename)
        with file(filename) as f:
            content = f.read()
        return content
