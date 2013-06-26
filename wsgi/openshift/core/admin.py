from django.contrib import admin
from core.models import Place
from core.models import UsersPlace
from core.models import Answer 
from core.models import Student 

admin.site.register(Place)
admin.site.register(UsersPlace)
admin.site.register(Answer)
admin.site.register(Student)

def updateStates():
    Place.objects.all().delete()
    file = open('usa.txt')
    states = file.read()
    ss = states.split("\n")
    for s in ss:
       state = s.split("\t")
       if(len(state) > 3):
          name = state[2]
          code = 'us-' + state[0].lower()
          Place(code=code, name = name).save()
    
def updateMap():
    Place.objects.all().delete()
    file = open('usa.txt')
    states = file.read()
    mapFile = open('usa.svg')
    map = mapFile.read()
    mapFile.close()
    ss = states.split("\n")
    for s in ss:
       state = s.split("\t")
       if(len(state) > 3):
          name = state[3]
          code = 'us-' + state[0].lower()
          map = map.replace(name, code);
    mapFile = open('usa.svg', 'w')
    mapFile.write(map)
