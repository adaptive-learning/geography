"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from core.models import Place, PlaceRelation
from django.test.client import Client
import json


class SimpleTest(TestCase):

    def test_basic_addition(self):
        """
        Tests
        """
        self.assertEqual(1 + 1, 2)
        c = Client()
        response = c.get('/question/world')
        self.assertEqual(response.status_code, 200)

        response_object = json.loads(response.content)

        places_of_world = PlaceRelation.objects.get(
            type=PlaceRelation.IS_ON_MAP,
            place__code="world"
            ).related_places.all()
        five_esiest_places = Place.objects.filter(
            id__in=places_of_world
            ).order_by("difficulty")[:5]

        self.assertEqual(response_object[0]["code"], five_esiest_places[0].code)
