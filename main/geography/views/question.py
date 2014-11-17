# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseBadRequest
from django.utils import simplejson
from django.utils.translation import ugettext as _
from geography.models import Place, PlaceRelation, UserPlace, AveragePlace, ABEnvironment
from proso_goals.models import Goal
from geography.utils import JsonResponse, QuestionService
from lazysignup.decorators import allow_lazy_user
from logging import getLogger
from ipware.ip import get_ip

LOGGER = getLogger(__name__)


@allow_lazy_user
def question(request, map_code, place_type_slug):
    try:
        map = PlaceRelation.objects.get(
            place__code=map_code,
            type=PlaceRelation.IS_ON_MAP)
    except PlaceRelation.DoesNotExist:
        raise Http404
    ABEnvironment.init_session(request.user, request.session)
    qs = QuestionService(user=request.user, map_place=map, ab_env=ABEnvironment(request))
    question_index = 0
    if request.raw_post_data:
        LOGGER.debug("processing raw answer %s", request.raw_post_data)
        answer = simplejson.loads(request.raw_post_data)
        qs.answer(answer, get_ip(request), request.LANGUAGE_CODE)
        question_index = answer['index'] + 1
    place_types = ([Place.PLACE_TYPE_SLUGS_LOWER_REVERSE[place_type_slug]]
                   if place_type_slug in Place.PLACE_TYPE_SLUGS_LOWER_REVERSE
                   else Place.CATEGORIES[place_type_slug]
                   if place_type_slug in Place.CATEGORIES
                   else [t[0] for t in Place.PLACE_TYPES])
    NUMBER_OF_QUESTIONS = 10
    response = {
        'questions': qs.get_questions(NUMBER_OF_QUESTIONS - question_index, place_types),
    }
    if question_index == NUMBER_OF_QUESTIONS:
        response['goals'] = [g.to_serializable() for g in
                             Goal.objects.for_user_and_map(request.user, map, place_types)]
    return JsonResponse(response)


def average_users_places(request, map_code):
    response = {}
    return JsonResponse(response)


@allow_lazy_user
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
        ps = UserPlace.objects.for_user_and_map_prepared(user, map, request.LANGUAGE_CODE)
    else:
        ps = []
    ps = list(ps)
    response = {
        'name': map.place.name,
        'placesTypes': [
            {
                'name': _(place_type[1]),
                'slug': Place.PLACE_TYPE_SLUGS_LOWER[place_type[0]],
                'places': [p.to_serializable() for p in ps
                           if hasattr(p, 'type') and p.type == place_type[0] or
                           not hasattr(p, 'type') and p.place.type == place_type[0]]
            } for place_type in Place.PLACE_TYPE_PLURALS
        ]
    }
    response['placesTypes'] = [pt for pt in response['placesTypes']
                               if len(pt['places']) > 0]
    LOGGER.info(
        u"users_places: previewed map '{0}' of user '{1}' with '{2}' places".
        format(map.place.name, user, len(list(ps))))
    return JsonResponse(response)
