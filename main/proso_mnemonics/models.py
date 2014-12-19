# -*- coding: utf-8 -*-
from django.db import models
from geography.models import Place
import settings


class Mnemonic(models.Model):
    LANGUAGES = [(i, code) for i, (code, name) in enumerate(settings.LANGUAGES)]
    LANGUAGES_REVERSE = dict((t[1], t[0]) for t in LANGUAGES)

    place = models.ForeignKey(Place)
    text = models.TextField()
    language = models.SmallIntegerField(choices=LANGUAGES, default=LANGUAGES[0][0])

    def to_serializable(self):
        return {
            'code': self.place.code,
            'text': self.text,
        }
