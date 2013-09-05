from questions.models import Answer, UsersPlace, ConfusedPlaces
from django.contrib import admin
from questions.utils import get_question_type_by_id, pretty_date

class UsersPlaceAdmin(admin.ModelAdmin):
    list_display = ('user', 'place')
    
class AnswerAdmin(admin.ModelAdmin):
    def is_correct(self, a):
        return a.place == a.answer
    is_correct.short_description = 'Is Correct'
    
    def question(self, a):
        return get_question_type_by_id(a.type).text
    question.short_description = 'Question'
    
    def asked_ago(self, a):
        return pretty_date(a.askedDate)
    asked_ago.short_description = 'When Asked'
    
    list_display = ( 'user','question', 'place', 'answer', 'is_correct', 'asked_ago')
    
class ConfusedPlacesAdmin(admin.ModelAdmin):
    list_display = ('asked', 'confused_with', 'level_of_cofusion')
    
admin.site.register(UsersPlace, UsersPlaceAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(ConfusedPlaces, ConfusedPlacesAdmin)
