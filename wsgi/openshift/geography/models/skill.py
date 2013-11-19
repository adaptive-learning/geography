# -*- coding: utf-8 -*-
from django.db import models
from place import Place
from django.contrib.auth.models import User


class LocalSkillManager(models.Manager):

    def from_user_and_place(self, user, place):
        try:
            return LocalSkill.objects.get(user=user, place=place)
        except LocalSkill.DoesNotExist:
            try:
                difficulty = Difficulty.objects.from_place(place).value
            except Difficulty.DoesNotExist:
                difficulty = 0
            try:
                skill = Skill.objects.from_user(user).value
                local_skill = skill - difficulty
            except Skill.DoesNotExist:
                local_skill = 0
        return LocalSkill(
            value=local_skill,
            user=user,
            place=place)


class LocalSkill(models.Model):

    value = models.FloatField(default=0)
    user = models.ForeignKey(User)
    place = models.ForeignKey(Place)
    objects = LocalSkillManager()

    class Meta:
        app_label = 'geography'


class DifficultyManager(models.Manager):

    def from_place(self, place):
        try:
            return Difficulty.objects.get(place=place)
        except Difficulty.DoesNotExist:
            return Difficulty(place=place)


class Difficulty(models.Model):

    value = models.FloatField(default=0)
    place = models.ForeignKey(Place)
    objects = DifficultyManager()

    class Meta:
        app_label = 'geography'


class SkillManager(models.Manager):

    def from_user(self, user):
        try:
            return Skill.objects.get(user=user)
        except Skill.DoesNotExist:
            return Skill(user=user)


class Skill(models.Model):

    value = models.FloatField(default=0)
    user = models.ForeignKey(User)
    objects = SkillManager()

    class Meta:
        app_label = 'geography'
