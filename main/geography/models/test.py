# -*- coding: utf-8 -*-
import logging
import random
import answer
import datetime
from place import Place
from django.db import models

LOGGER = logging.getLogger(__name__)


class TestManager(models.Manager):

    def get_test_places(self, user_id, place_map_id, place_types, n):
        already_passed = self._get_already_passed_test_ids(user_id, place_map_id, place_types)
        passed_test_ids, passed_place_types = zip(*already_passed) if already_passed else ([], [])
        passed_test_ids = list(passed_test_ids)
        available = self._get_available_test_ids(
            user_id, place_map_id, place_types, passed_place_types)
        in_this_session = self._get_asked_place_test_ids_for_this_session(
            user_id, passed_test_ids)
        candidate_test_ids =  list(
            set(self._get_place_active_test_ids(passed_test_ids + available))
            -
            set(in_this_session))
        candidate_ids, test_ids = zip(*candidate_test_ids) if candidate_test_ids else ([], [])
        return zip(Place.objects.filter(id__in=candidate_ids), test_ids)

    def init(self, place_map, place_type, test_size):
        place_ids = Place.objects.get_place_ids_on_map(place_map, [place_type])
        places = list(Place.objects.filter(id__in=place_ids))
        random.shuffle(places)
        num_groups = len(places) / test_size
        groups = []
        for i in range(num_groups):
            groups.append(places[(i * test_size):((i+1) * test_size)])
        remains = len(places) % test_size
        if remains > 0:
            last_group = places[-remains:]
            last_group = last_group + random.sample(places, test_size - remains)
            groups.append(last_group)
        for g in groups:
            test = Test(
                place_test_map=place_map.place,
                place_type=place_type)
            test.save()
            for p in g:
                test.places_to_ask.add(p)
            test.save()
        return groups

    def _get_already_passed_test_ids(self, user_id, place_map_id, place_types):
        return list(answer.Answer.objects.
            filter(
                test__id__isnull=False,
                place_map_id=place_map_id,
                user_id=user_id,
                place_asked__type__in=place_types).
            values_list('test__id', 'test__place_type').
            distinct())

    def _get_available_test_ids(self, user_id, place_map_id, place_types, place_types_exclude):
        available = list(self.
            filter(
                place_test_map_id=place_map_id,
                place_type__in=place_types).
            exclude(place_type__in=place_types_exclude).
            values('id', 'place_type'))
        available_dict = {}
        for row in available:
            avail_type = available_dict.get(row['place_type'], [])
            avail_type.append(row['id'])
            available_dict[row['place_type']] = avail_type
        return [random.choice(ids) for place_type, ids in available_dict.items()]

    def _get_asked_place_test_ids_for_this_session(self, user_id, test_ids):
        return list(answer.Answer.objects
            .filter(
                test__id__in=test_ids,
                user_id=user_id,
                inserted__gt=(datetime.datetime.now() - datetime.timedelta(minutes=30))).
            values_list('place_asked__id', 'test__id'))

    def _get_place_active_test_ids(self, test_ids):
        return list(self.
            filter(
                id__in=test_ids,
                active=True).
            values_list('places_to_ask__id', 'id'))


class Test (models.Model):

    active = models.BooleanField(default=True)
    place_test_map = models.ForeignKey(Place, related_name='place_test_map_id')
    place_type = models.IntegerField(choices=Place.PLACE_TYPES)
    places_to_ask = models.ManyToManyField(Place)

    objects = TestManager()

    class Meta:
        app_label = 'geography'
