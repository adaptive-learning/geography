# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseBadRequest
from django.utils import simplejson
from geography.models import Place, PlaceRelation, UserPlace, AveragePlace
from geography.utils import JsonResponse, QuestionService
from lazysignup.decorators import allow_lazy_user
from logging import getLogger
import geography.models.user
import math

LOGGER = getLogger(__name__)


@allow_lazy_user
def question(request, map_code, place_type_slug):
    try:
        map = PlaceRelation.objects.get(
            place__code=map_code,
            type=PlaceRelation.IS_ON_MAP)
    except PlaceRelation.DoesNotExist:
        raise Http404
    qs = QuestionService(user=request.user, map_place=map)
    question_index = 0
    if request.raw_post_data:
        LOGGER.debug("processing raw answer %s", request.raw_post_data)
        answer = simplejson.loads(request.raw_post_data)
        qs.answer(answer)
        question_index = answer['index'] + 1
    if should_get_questions(request, question_index):
        place_type = (Place.PLACE_TYPE_SLUGS_LOWER_REVERSE[place_type_slug]
                      if place_type_slug in Place.PLACE_TYPE_SLUGS_LOWER_REVERSE
                      else -1)
        response = qs.get_questions(10 - question_index, place_type)
    else:
        response = []
    return JsonResponse(response)


def should_get_questions(request, question_index):
    points = geography.models.user.get_points(request.user)
    return ((points <= 10
            or question_index % math.ceil(math.log(points, 10)) == 0)
            and question_index != 9)


def average_users_places(request, map_code):

    response = {}
    return JsonResponse(response)


def users_places(request, map_code, user=None):

    try:
        map = PlaceRelation.objects.get(
            place__code=map_code,
            type=PlaceRelation.IS_ON_MAP)
        map_places = map.related_places.all()
    except PlaceRelation.DoesNotExist:
        raise Http404("Unknown map name: {0}".format(map_code))
    try:
        too_small_places = PlaceRelation.objects.get(
            place__code=map_code,
            type=PlaceRelation.IS_TOO_SMALL_ON_MAP)
        map_places = map_places | too_small_places.related_places.all()
    except PlaceRelation.DoesNotExist:
        pass


    if not user:
        user = request.user
    elif user == "average":
        pass
    else:
        try:
            user = User.objects.get(username=user)
        except User.DoesNotExist:
            raise HttpResponseBadRequest("Invalid username: {0}" % user)

    if user == "average":
        ps = AveragePlace.objects.for_map(map_places)
    elif request.user.is_authenticated():
        ps = UserPlace.objects.for_user_and_map(user, map_places)
    else:
        ps = []
    response = {
        'name': map.place.name,
        'placesTypes': [
            {
                'name': place_type[1],
                'slug': Place.PLACE_TYPE_SLUGS_LOWER[place_type[0]],
                'places': [p.to_serializable() for p in ps
                           if p.place.type == place_type[0]]
            } for place_type in Place.PLACE_TYPE_PLURALS
        ]
    }
    response['placesTypes'] = [pt for pt in response['placesTypes']
                               if len(pt['places']) > 0]
    LOGGER.info(
        u"users_places: previewed map '{0}' of user '{1}' with '{2}' places".
        format(map.place.name, user, len(ps)))
    return JsonResponse(response)
