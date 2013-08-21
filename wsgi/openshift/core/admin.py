from core.models import Answer, Place, Student, UsersPlace, ConfusedPlaces, Map
from django.contrib import admin

class UsersPlaceAdmin(admin.ModelAdmin):
    list_display = ('user', 'place')
    
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'difficulty')
    
class AnswerAdmin(admin.ModelAdmin):
    def is_correcttype(self, a):
        return a.place == a.answer
    is_correcttype.short_description = 'Is Correct'
    list_display = ( 'user', 'place', 'answer', 'is_correct' 'type', 'askedDate')
    
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'skill')
    
class ConfusedPlacesAdmin(admin.ModelAdmin):
    list_display = ('asked', 'confused_with', 'level_of_cofusion')
    
admin.site.register(Place, PlaceAdmin)
admin.site.register(UsersPlace, UsersPlaceAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(ConfusedPlaces, ConfusedPlacesAdmin)
admin.site.register(Map)

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
