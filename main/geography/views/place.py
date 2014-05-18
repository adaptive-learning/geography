# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseBadRequest
from geography.models import Place, PlaceRelation, MapSkill
from geography.utils import JsonResponse
from django.views.decorators.cache import cache_page


def _places(request, map_code):
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

    response = {
        'name': map.place.name,
        'slug': map.place.code,
        'placesTypes': [
            {
                'name': place_type[1],
                'slug': Place.PLACE_TYPE_SLUGS_LOWER[place_type[0]],
                'count': len([p for p in map_places
                             if p.type == place_type[0]])
            } for place_type in Place.PLACE_TYPE_PLURALS
        ]
    }
    response['placesTypes'] = [pt for pt in response['placesTypes']
                               if pt['count'] > 0]
    return response


@cache_page(60 * 60)
def places_overview(request):
    map_types = [{
        'name': 'Svět',
        'maps': Place.objects.filter(code='world'),
    }, {
        'name': 'Kontinenty',
        'maps': Place.objects.get_continents(),
    }, {
        'name': 'Státy',
        'maps': Place.objects.get_states_with_map(),
    }]
    for map_type in map_types:
        map_type['maps'] = [_places(request, m.code) for m in map_type['maps']]
    return JsonResponse(map_types)


def mapskill(request, user=None):
    if not user:
        user = request.user
    else:
        try:
            user = User.objects.get(username=user)
        except User.DoesNotExist:
            raise HttpResponseBadRequest("Invalid username: {0}" % user)
    maps_skills = MapSkill.objects.for_user(user)
    return JsonResponse([m.to_serializable() for m in maps_skills])
