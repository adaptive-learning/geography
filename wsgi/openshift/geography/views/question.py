# -*- coding: utf-8 -*-
from geography.utils import JsonResponse
from geography.models import User, Place
from django.http import Http404, HttpResponseBadRequest
from django.utils import simplejson
from lazysignup.decorators import allow_lazy_user
from geography.models import PlaceRelation, UserPlace
from geography.utils import QuestionService
from logging import getLogger


logger = getLogger(__name__)


@allow_lazy_user
def question(request, map_code):
    try:
        map = PlaceRelation.objects.get(
            place__code=map_code,
            type=PlaceRelation.IS_ON_MAP)
    except PlaceRelation.DoesNotExist:
        raise Http404
    qs = QuestionService(user=request.user, map_place=map)
    if request.raw_post_data:
        answer = simplejson.loads(request.raw_post_data)
        qs.answer(answer)
    response = qs.get_questions(10)
    return JsonResponse(response)


def users_places(request, map_code, user=None):
    try:
        map = PlaceRelation.objects.get(
            place__code=map_code,
            type=PlaceRelation.IS_ON_MAP)
    except PlaceRelation.DoesNotExist:
        raise Http404("Unknown map name: {0}".format(map_code))
    if not user:
        user = request.user
    else:
        try:
            user = User.objects.get(username=user)
        except User.DoesNotExist:
            raise HttpResponseBadRequest("Invalid username: {0}" % user)

    if request.user.is_authenticated():
        ps = UserPlace.objects.for_user_and_map(user, map)
    else:
        ps = []
    try:
        cs = PlaceRelation.objects.get(
            place__code=map_code,
            type=PlaceRelation.IS_SUBMAP,
        ).related_places.all()
    except PlaceRelation.DoesNotExist:
        cs = []
    response = {
        'name': map.place.name,
        'placesTypes': [
            {
                'name': u'Jezera',
                'slug': 'lakes',
                'places': [p.to_serializable() for p in ps if p.place.type == Place.LAKE]
            }, {
                'name': u'Města',
                'slug': 'cities',
                'places': [p.to_serializable() for p in ps if p.place.type == Place.CITY]
            }, {
                'name': u'Státy',
                'slug': 'states',
                'places': [p.to_serializable() for p in ps if p.place.type == Place.STATE]
            }, {
                'name': u'Řeky',
                'slug': 'rivers',
                'places': [p.to_serializable() for p in ps if p.place.type == Place.RIVER]
            }
        ]
    }
    logger.info(
        u"users_places: previewed map '{0}' of user '{1}' with '{2}' places".
        format(map.place.name, user, len(cs)))
    return JsonResponse(response)
