# -*- coding: utf-8 -*-
# Create your views here.
from django.http import HttpResponse
from django.utils import simplejson
from random import randint
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import os

from core.models import Place
from core.models import Answer 
from core.models import Student 
from core.models import UsersPlace 

class JsonResponse(HttpResponse):
    """
        JSON response
    """
    def __init__(self, content, mimetype='application/json', status=None, content_type=None):
        super(JsonResponse, self).__init__(
            content=simplejson.dumps(content),
            mimetype=mimetype,
            status=status,
            content_type=content_type,
        )

class QuestionService():

    @staticmethod
    def getQuestion():
        questionTypes = [
                u"Vyber na mapě stát",
                u"Jak se jmenuje stát zvýrazněný na mapě?"
            ]
        ps = Place.objects.all()
        place = ps[randint(0,len(ps) -1)]
        type = randint(0,1)
        question = {
            'type' : type,
            'text' : questionTypes[type], 
            'place' :  place.name,
            'code' : place.code
        }
        return question

    @staticmethod
    def answer(a):
        student = Student.fromUser(a["user"])
        place = Place.objects.get(code = a["code"])
        answerPlace = Place.objects.get(code = a["answer"]) if a["answer"] != "" else None
        Answer(
            user = student, 
            place = place,
            answer = answerPlace,
            type = a["type"],
            msResposeTime = a["msResponseTime"] 
        ).save()
        student.points += 1;
        student.save();
        usersPlace = UsersPlace.fromStudentAndPlace(student, place)
        usersPlace.askedCount += 1
        if (place == answerPlace):
            usersPlace.correctlyAnsweredCount += 1
        usersPlace.save()

def places(request):
    ps = Place.objects.all()
    response = [{
        'name': u'Státy',
        'places': []
    }]
    for p in ps:
        response[0]['places'].append({
          'code' : p.code,
          'name' : p.name
        })
    return JsonResponse(response)

def question(request):
    if (request.raw_post_data != ""):
        answer = simplejson.loads(request.raw_post_data)
        answer["user"] = request.user
        QuestionService.answer(answer);

    response = []
    for i in range(0, 10):
        response.append(QuestionService.getQuestion())
    return JsonResponse(response)

def user_view(request):
    student = Student.fromUser(request.user)
    if (student != None):
        response = {
            'username' : student.user.username,
            'points' :  student.points
        }
    else:
        response = {
            'username' : '',
            'points' : 0 
        }
    #updateStates()
    #updateMap()
    return JsonResponse(response)

def login_view(request):
    if (request.raw_post_data != ""):
        credentials = simplejson.loads(request.raw_post_data)
        user = authenticate(
            username=credentials["username"], 
            password=credentials["password"],
        )
        if user is not None:
            if user.is_active:
                login(request, user)
                # Redirect to a success page.
            #else:
                # Return a 'disabled account' error message
        #else:
            # Return an 'invalid login' error message.
    return user_view(request)
    
def logout_view(request):
    logout(request)
    return user_view(request)
    

def updateStates_view(request):
    if (Place.objects.count() == 0):
        updateStates();
    return HttpResponse("states Updated")

def updateStates():
    Place.objects.all().delete()
    file = open('app-root/runtime/repo/usa.txt')
    states = file.read()
    ss = states.split("\n")
    for s in ss:
       state = s.split("\t")
       if(len(state) > 3):
          name = state[2]
          code = 'us-' + state[0].lower()
          Place(code=code, name = name).save()
