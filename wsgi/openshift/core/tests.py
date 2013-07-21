"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from django.utils import simplejson

from django.contrib.auth.models import User

from core.models import Place
from core.models import Answer 
from core.models import Student 
from core.models import UsersPlace 
from core.views import QuestionService 


class UsersPlaceTest(TestCase):

    def setUp(self):
        user = User.objects.create_user(
            'john',
            'lennon@thebeatles.com',
            'johnpassword'
        )
        student = Student.fromUser(user)
        place = Place(
            code='ca', 
            name = 'Canada'
        )
        place.save()

        self.usersPlace = UsersPlace(
            user = student, 
            place = place,
        )
        self.usersPlace.save()

    def testSkill(self):
        """
        Tests that skill is 0 if all answers were wrong
        and 1 if all were correct
        """
        usersPlace = self.usersPlace 
        usersPlace.askedCount += 1
        self.assertEqual(usersPlace.skill(), 0)

        usersPlace.correctlyAnsweredCount += 1
        self.assertEqual(usersPlace.skill(), 1)
        
class QuestionServiceTest(TestCase):

    def setUp(self):

        place = Place(
            code='ca', 
            name = 'Canada',
            difficulty = int(0.2 * Place.DIFFICULTY_CONVERSION)
        )
        place.save()

        place = Place(
            code='bz', 
            name = 'Belize',
            difficulty = int(0.9 * Place.DIFFICULTY_CONVERSION)
        )
        place.save()

        user = User.objects.create_user(
            'john',
            'lennon@thebeatles.com',
            'johnpassword'
        )
        user.save()
        self.qs = QuestionService(user)

    def testQuestion(self):
        questions = self.qs.getQuestions(5)
        self.assertEqual(len(questions), 2)
        self.assertEqual(questions[0]['code'], 'ca')
