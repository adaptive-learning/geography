# -*- coding: utf-8 -*-
from django.conf import settings


class StaticFiles():

    @staticmethod
    def add_hash(files):
        return [f + "?hash=" + StaticFiles.get_hash_od_file(f) for f in files]

    @staticmethod
    def get_hash_od_file(f):
        return settings.HASHES[f] if f in settings.HASHES else ""
