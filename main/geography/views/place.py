# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from geography.models import Place, PlaceRelation, MapSkill
from geography.utils import JsonResponse
from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404


def _places(request, map_code):
    map = get_object_or_404(PlaceRelation,
                            place__code=map_code,
                            type=PlaceRelation.IS_ON_MAP)
    map_places = map.related_places.all()
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
                'name': unicode(place_type[1]),
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
        'name': 'World',  # not translated on purpose
        'maps': Place.objects.filter(code='world'),
    }, {
        'name': _('Kontinenty'),
        'maps': Place.objects.get_continents(),
    }, {
        'name': _(u'Státy'),
        'maps': Place.objects.get_states_with_map(request),
    }]
    for map_type in map_types:
        map_type['maps'] = [_places(request, m.code) for m in map_type['maps']]
    return JsonResponse(map_types)


def mapskill(request, user=None):
    if not user:
        user = request.user
    else:
        user = get_object_or_404(User, username=user)
    maps_skills = MapSkill.objects.for_user(user)
    return JsonResponse([m.to_serializable() for m in maps_skills])
