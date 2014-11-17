from models import Goal
from django.contrib import admin


class GoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'map', 'place_type', 'start_date', 'finish_date')


admin.site.register(Goal, GoalAdmin)
