# -*- coding: utf-8 -*-

from core.models import Place, Student, UsersPlace
from core.utils import QuestionService
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import simplejson
from lazysignup.decorators import allow_lazy_user
from lazysignup.utils import is_lazy_user



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

# Create your views here.
def places(request):
    ps = Place.objects.all().order_by('name')
    response = [{
        'name': u'Státy',
        'places': [p.toSerializable() for p in ps]
    }]
    return JsonResponse(response)

@allow_lazy_user
def users_places(request, part,  user = ''):
    if (user == ''):
        user = request.user
    else:
        try:
            user = User.objects.get(username = user)
        except User.DoesNotExist:
            raise HttpResponseBadRequest("Invalid username: {0}" % user)
    student = Student.fromUser(user)
    ps = UsersPlace.objects.filter(user=student)
    response = [{
        'name': u'Státy',
        'places': []
    }]
    for p in ps:
        response[0]['places'].append({
          'code' : p.place.code,
          'name' : p.place.name,
          'skill' : p.skill(),
        })
    return JsonResponse(response)

@allow_lazy_user
def question(request):
    qs = QuestionService(user = request.user)
    questionIndex = 0
    if (request.raw_post_data != ""):
        answer = simplejson.loads(request.raw_post_data)
        questionIndex = answer['index'] + 1
        qs.answer(answer);
    noOfQuestions = 5 if Student.fromUser(request.user).points < 10 else 10
    noOfQuestions -= questionIndex
    response = qs.getQuestions(noOfQuestions)
    return JsonResponse(response)

def to_view_format(student):
    newObj = {
        'username' : student.user.username,
        'points' :  student.points,
    }
    return newObj

@allow_lazy_user
def user_list_view(request):
    students = Student.objects.all()
    response = [to_view_format(s) for s in students if not is_lazy_user(s.user)]
    return JsonResponse(response)
    
@allow_lazy_user
def user_view(request):
    student = Student.fromUser(request.user)
    isRegistredUser = not is_lazy_user(request.user)
    username = student.user.username if isRegistredUser else ''
    response = {
        'username' : username,
        'points' :  student.points,
    }
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
                response = {'success' : True }
            else:
                # Return a 'disabled account' error message
                response = {
                    'success' : False,
                    'message' : 'Přihlašovací údaje jsou správné, ale účet je zablokován'
                }
        else:
            # Return an 'invalid login' error message.
            response = {
                'success' : False,
                'message' : 'Nesprávné uživatelské jméno nebo heslo.'
            }
    return JsonResponse(response)
    
def logout_view(request):
    logout(request)
    return user_view(request)
    

def updateStates_view(request):
    if (Place.objects.count() == 0):
        updateStates();
    else:
        states = Place.objects.all()
        [ s.updateDifficulty() for s in states ]
    return HttpResponse("states Updated")

def updateStates():
    Place.objects.all().delete()
    statesFile = open('app-root/runtime/repo/usa.txt')
    states = statesFile.read()
    ss = states.split("\n")
    for s in ss:
        state = s.split("\t")
        if(len(state) > 3):
            name = state[2]
            code = 'us-' + state[0].lower()
            Place(code=code, name = name).save()
