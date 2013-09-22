# -*- coding: utf-8 -*-

from accounts.models import Student
from core.utils import JsonResponse
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseBadRequest, HttpResponse
from django.utils import simplejson
from lazysignup.decorators import allow_lazy_user
from questions.models import PlaceRelation, UsersPlace
from questions.utils import QuestionService

# Create your views here.
@allow_lazy_user
def question(request, map_code):
    try:
        map = PlaceRelation.objects.get(place__code=map_code, type=PlaceRelation.IS_ON_MAP)
    except PlaceRelation.DoesNotExist:
        raise Http404
    student = Student.objects.fromUser(request.user)
    qs = QuestionService(user=student, map=map)
    questionIndex = 0
    if (request.raw_post_data != ""):
        answer = simplejson.loads(request.raw_post_data)
        questionIndex = answer['index'] + 1
        qs.answer(answer);
    noOfQuestions = 5 if student.points < 10 else 10
    noOfQuestions -= questionIndex
    response = qs.get_questions(noOfQuestions)
    return JsonResponse(response)

def users_places(request, map_code, user=''):
    try:
        map = PlaceRelation.objects.get(place__code=map_code, type=PlaceRelation.IS_ON_MAP)
    except PlaceRelation.DoesNotExist:
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
           place_id__in=map.related_places.all()
       ).select_related().order_by("place__name")
    else:
        ps =[]
    try:
        cs = PlaceRelation.objects.get(
           place__code=map_code,
           type=PlaceRelation.IS_SUBMAP,
        ).related_places.all()
    except PlaceRelation.DoesNotExist:
        cs = []
    response = {
        'name' : map.place.name,
        'placesTypes' : [{
            'name': u'Kontinenty',
            'haveMaps': True,
            'places': [p.to_serializable() for p in cs]
        },{
            'name': u'Státy',
            'places': [p.to_serializable() for p in ps]
        }]
        }
    return JsonResponse(response)
    
