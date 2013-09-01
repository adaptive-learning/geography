from core.models import Answer, Place, Student, UsersPlace, ConfusedPlaces, PlaceRelation
from django.contrib import admin
from core.utils import get_question_type_by_id

class UsersPlaceAdmin(admin.ModelAdmin):
    list_display = ('user', 'place')
    
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'difficulty')
    
class AnswerAdmin(admin.ModelAdmin):
    def is_correct(self, a):
        return a.place == a.answer
    is_correct.short_description = 'Is Correct'
    
    def question(self, a):
        return get_question_type_by_id(a.type).text
    question.short_description = 'Question'
    
    list_display = ( 'user','question', 'place', 'answer', 'is_correct', 'askedDate')
    
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'skill')
    
class ConfusedPlacesAdmin(admin.ModelAdmin):
    list_display = ('asked', 'confused_with', 'level_of_cofusion')
class PlaceRelationAdmin(admin.ModelAdmin):
    list_display = ('place', 'type')
    
admin.site.register(Place, PlaceAdmin)
admin.site.register(UsersPlace, UsersPlaceAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(ConfusedPlaces, ConfusedPlacesAdmin)
admin.site.register(PlaceRelation, PlaceRelationAdmin)

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
