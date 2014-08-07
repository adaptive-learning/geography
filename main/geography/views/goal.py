# -*- coding: utf-8 -*-
from geography.utils import JsonResponse
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseBadRequest
from django.utils import simplejson
from geography.models import Goal, Place, PlaceRelation, MapSkill


def goals_delete(request, id):
    Goal.objects.filter(id=id, user=request.user).delete()
    return JsonResponse({})


def goals_add(request, username=None):
    goal_dict = simplejson.loads(request.body)
    try:
        map_relation = PlaceRelation.objects.get(
            place=Place.objects.get(code=goal_dict.get('map')),
            type=PlaceRelation.IS_ON_MAP)
    except Place.DoesNotExist:
        raise HttpResponseBadRequest("Invalid place code: {0}".format(goal_dict.get('map')))
    except PlaceRelation.DoesNotExist:
        raise HttpResponseBadRequest("No map for place code: {0}".format(goal_dict.get('map')))
    try:
        place_type = Place.PLACE_TYPE_SLUGS_LOWER_REVERSE[goal_dict['layer']]
    except KeyError:
        raise HttpResponseBadRequest("Invalid place type slug: {0}".format(goal_dict.get('layer')))
    map_skill = MapSkill.objects.for_user_and_map_and_type(request.user, map_relation, place_type)
    if map_skill.goal_probability == Goal.GOAL_PROBABILITY:
        raise HttpResponseBadRequest("The goal is already reached")
    goal = Goal(
        user=request.user,
        finish_date=goal_dict['finish_date'].split('T')[0],
        map=map_relation,
        place_type=place_type,
        start_probability=map_skill.goal_probability,
    )
    goal.save()
    response = {
        'type': 'success',
        'msg': u'Cíl byl vytvořen',
    }
    return JsonResponse(response)


def goals_view(request, username=None):
    if request.method == "POST":
        return goals_add(request, username)
    else:
        if not username:
            user = request.user
        else:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise Http404("Invalid username: {0}".format(username))
        response = Goal.objects.for_user(user)
        response = map((lambda x: x.to_serializable()), response)
        return JsonResponse(response)
