# -*- coding: utf-8 -*-
from geography.utils import JsonResponse
from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest
from django.utils import simplejson
from geography.models import Place, PlaceRelation, MapSkill
from proso_goals.models import Goal
from proso_goals.utils import get_reminder_email
from django.http import HttpResponse
from django.shortcuts import get_object_or_404


def goals_delete(request, id):
    Goal.objects.filter(id=id, user=request.user).delete()
    return JsonResponse({})


def goals_add(request, username=None):
    goal_dict = simplejson.loads(request.body)
    place = get_object_or_404(Place, code=goal_dict.get('map'))
    map_relation = get_object_or_404(PlaceRelation,
                                     place=place,
                                     type=PlaceRelation.IS_ON_MAP)
    try:
        place_type = Place.PLACE_TYPE_SLUGS_LOWER_REVERSE[goal_dict['layer']]
    except KeyError:
        return HttpResponseBadRequest("Invalid place type slug: {0}".format(goal_dict.get('layer')))
    map_skill = MapSkill.objects.for_user_and_map_and_type(request.user, map_relation, place_type)
    if map_skill.goal_probability >= Goal.GOAL_PROBABILITY:
        return HttpResponseBadRequest("The goal is already reached")
    goal = Goal(
        user=request.user,
        finish_date=goal_dict['finish_date'].split('T')[0],
        map=map_relation,
        place_type=place_type,
        start_probability=map_skill.goal_probability,
    )
    goal.save()
    goal = Goal.objects.get(id=goal.id)
    goal.probability = goal.start_probability
    return JsonResponse(goal.to_serializable())


def goals_view(request, username=None):
    if request.method == "POST":
        return goals_add(request, username)
    else:
        if not username:
            user = request.user
        else:
            user = get_object_or_404(User, username=username)
        response = Goal.objects.for_user(user)
        response = map((lambda x: x.to_serializable()), response)
        return JsonResponse(response)


def reminder_email(request, username=None):
    if not username:
        user = request.user
    else:
        user = get_object_or_404(User, username=username)
    goals = [g.to_serializable() for g in
             Goal.objects.goals_behind_schedule(user)]
    email = get_reminder_email(goals, user)
    email_text = email[0 if 'plain' in request.GET else 1]
    return HttpResponse(email_text)
