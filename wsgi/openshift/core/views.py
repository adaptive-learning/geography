# -*- coding: utf-8 -*-

from core.models import Place, Student, UsersPlace, Map
from core.utils import QuestionService, JsonResponse
from django.conf import settings
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.utils import simplejson
from lazysignup.decorators import allow_lazy_user



# Create your views here.
def home(request):
    request.META["CSRF_COOKIE_USED"] = True
    title = 'Loc - ' if not settings.ON_OPENSHIFT else ''
    c = {
         'title' : title,
         'isProduction' : settings.ON_OPENSHIFT,
    }
    c.update(csrf(request))
    return render_to_response('home/home.html', c)

def users_places(request, map_code, user=''):
    try:
        map = Map.objects.get(name=map_code)
    except Map.DoesNotExist:
        raise Http404("Unknown map name: {0}".format(map_code))
    if (user == ''):
        user = request.user
    else:
        try:
            user = User.objects.get(username=user)
        except User.DoesNotExist:
            raise HttpResponseBadRequest("Invalid username: {0}" % user)
        
    if request.user.is_authenticated():
        student = Student.objects.fromUser(user)
        ps = UsersPlace.objects.filter(
           user=student,
           place_id__in=map.places.all()
       )
    else:
        ps =[]
    response = [{
        'name': u'Státy',
        'places': []
    }]
    for p in ps:
        response[0]['places'].append(p.to_serializable())
    return JsonResponse(response)

@allow_lazy_user
def question(request, map_code):
    try:
        map = Map.objects.get(name=map_code)
    except Map.DoesNotExist:
        raise Http404
    qs = QuestionService(user=request.user, map=map)
    questionIndex = 0
    if (request.raw_post_data != ""):
        answer = simplejson.loads(request.raw_post_data)
        questionIndex = answer['index'] + 1
        qs.answer(answer);
    noOfQuestions = 5 if Student.objects.fromUser(request.user).points < 10 else 10
    noOfQuestions -= questionIndex
    response = qs.get_questions(noOfQuestions)
    return JsonResponse(response)

