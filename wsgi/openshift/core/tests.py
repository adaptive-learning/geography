"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from django.contrib.auth.models import User

from core.models import Place
from core.models import Answer 
from core.models import Student 
from core.models import UsersPlace 


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

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
        

