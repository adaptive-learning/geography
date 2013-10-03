"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from core.models import PlaceRelation
from accounts.models import StudentManager
from questions.models import Answer, Place, Student, UsersPlace
from questions.utils import QuestionService
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from django.utils import simplejson


class UsersPlaceTest(TestCase):

    def setUp(self):
        user = User.objects.create_user(
            'john',
            'lennon@thebeatles.com',
            'johnpassword'
        )
        student = Student.objects.fromUser(user)
        place = Place(
            code='ca',
            name='Canada',
            type=Place.STATE
        )
        place.save()

        self.usersPlace = UsersPlace(
            user=student,
            place=place,
        )
        self.usersPlace.save()

    def testSkill(self):
        """
        Tests that skill is 0 if all answers were wrong
        and 1 if all were correct
        """
        usersPlace = self.usersPlace
        usersPlace.askedCount += 1
        self.assertEqual(usersPlace.get_skill(), 0)

        usersPlace.correctlyAnsweredCount += 1
        self.assertEqual(usersPlace.get_skill(), 1)


class QuestionServiceTest(TestCase):

    def setUp(self):

        map = Place(
            code='w',
            name='World',
            type=Place.WORLD
        )
        map.save()

        canada = Place(
            code='ca',
            name='Canada',
            difficulty=int(0.2 * Place.DIFFICULTY_CONVERSION),
            type=Place.STATE
        )
        canada.save()

        belize = Place(
            code='bz',
            name='Belize',
            difficulty=int(0.9 * Place.DIFFICULTY_CONVERSION),
            type=Place.STATE
        )
        belize.save()

        on_map = PlaceRelation(
            place=map,
            type=PlaceRelation.IS_ON_MAP
        )
        on_map.save()
        on_map.related_places.add(canada)
        on_map.related_places.add(belize)
        on_map.save()

        user = User.objects.create_user(
            'john',
            'lennon@thebeatles.com',
            'johnpassword'
        )
        user.save()
        student = Student.objects.fromUser(user)
        self.qs = QuestionService(student, on_map)

    def testQuestion(self):
        questions = self.qs.get_questions(2)
        self.assertEqual(len(questions), 2)
        self.assertEqual(questions[0]['code'], 'ca')
