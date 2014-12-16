# -*- coding: utf-8 -*-
from django.db import models
from geography.models import PlaceRelation, Place, MapSkill
from django.contrib.auth.models import User
from datetime import date, timedelta
import datetime


class GoalManager(models.Manager):
    def for_user(self, user):
        goals = self.filter(user=user.id)
        goals = self.fetch_probability_and_place_count(user, goals)
        return goals

    def for_user_and_map(self, user, map, place_type):
        goals = self.filter(
            user=user,
            map=map,
            place_type__in=place_type)
        goals = self.fetch_probability_and_place_count(user, goals)
        return goals

    def fetch_probability_and_place_count(self, user, goals):
        maps_skills = MapSkill.objects.for_user(user)
        for g in goals:
            for ms in maps_skills:
                if g.map.place.code == ms.code and g.place_type == ms.type:
                    g.probability = ms.goal_probability
                    g.place_count = ms.count
                    if g.probability < g.start_probability:
                        g.start_probability = g.probability
                        g.save()
        return goals

    def goals_behind_schedule(self, user=None):
        goals = Goal.objects.filter(
            finish_date__gt=datetime.date.today()
        ).select_related('user')
        if user is not None:
            goals = goals.filter(
                user=user,
            )
        goals = [g for g in goals if g.behind_schedule]
        return goals


class Goal(models.Model):
    GOAL_PROBABILITY=0.9
    start_date = models.DateField(auto_now_add=True)
    finish_date = models.DateField()
    start_probability = models.FloatField(default=0.5)
    map = models.ForeignKey(PlaceRelation)
    place_type = models.IntegerField(choices=Place.PLACE_TYPES, default=Place.UNKNOWN)
    user = models.ForeignKey(User)

    probability = 0
    place_count = 0

    objects=GoalManager()

    def to_serializable(self):
        return {
            'id': self.id,
            'start_date': str(self.start_date),
            'finish_date': str(self.finish_date),
            'map': self.map.place.to_serializable(),
            'type': {
                'slug': Place.PLACE_TYPE_SLUGS_LOWER[self.place_type],
                'name': unicode(Place.PLACE_TYPE_PLURALS[self.place_type][1]),
            },
            'probability': self.probability,
            'progress': self.progress,
            'expected_progress': self.expected_progress,
            'expected_progress_yesterday': self.expected_progress_yesterday,
            'behind_schedule': self.behind_schedule,
            'needs_practice': round(self.progress, 3) < self.expected_progress,
            'can_be_deleted': self.start_date == date.today(),
            'progress_diff': self.expected_progress - self.progress,
        }

    @property
    def behind_schedule(self):
        return round(self.progress, 3) < self.expected_progress_yesterday

    @property
    def expected_progress_yesterday(self):
        before_start = self.start_date - timedelta(days=1)
        numerator = (date.today() - self.start_date).total_seconds()
        denominator = (self.finish_date - before_start).total_seconds()
        ratio = numerator / denominator
        return max(0, min(ratio, 1))

    @property
    def expected_progress(self):
        before_start = self.start_date - timedelta(days=1)
        numerator = (date.today() - before_start).total_seconds()
        denominator = (self.finish_date - before_start).total_seconds()
        ratio = numerator / denominator
        return max(0, min(ratio, 1))

    @property
    def progress(self):
        numerator = self.probability - self.start_probability
        denominator = self.GOAL_PROBABILITY - self.start_probability
        ratio = numerator / denominator
        return max(0, min(ratio, 1))

    class Meta:
        unique_together = ('user', 'map', 'place_type')
        ordering = ["-id"]
