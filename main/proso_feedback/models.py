from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


class Rating(models.Model):
    UNKNOWN = 0
    EASY = 1
    RIGHT = 2
    HARD = 3
    VALUES = (
        (UNKNOWN, 'Unknown'),
        (EASY, 'Too Easy'),
        (RIGHT, 'Just Right'),
        (HARD, 'Too Hard'),
    )
    user = models.ForeignKey(User)
    inserted = models.DateTimeField(default=datetime.now)
    value = models.SmallIntegerField(choices=VALUES, default=UNKNOWN)
