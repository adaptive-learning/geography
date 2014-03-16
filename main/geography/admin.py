# -*- coding: utf-8 -*-

from models import Place, PlaceRelation, Answer, PriorSkill, CurrentSkill, Difficulty
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect


################################################################################
# functions

def export_selected_objects(modeladmin, request, queryset):
    selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
    ct = ContentType.objects.get_for_model(queryset.model)
    return (
        HttpResponseRedirect(
            "/export/?model=%s.%s&ids=%s" %
            (ct.app_label, ct.model, ",".join(selected)))
    )


def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = datetime.now()
    if isinstance(time, int):
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time, datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(second_diff / 60) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(second_diff / 3600) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff / 7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff / 30) + " months ago"
    return str(day_diff / 365) + " years ago"


################################################################################
# classes


class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'type')
    list_filter = ('type',)


class PlaceRelationAdmin(admin.ModelAdmin):
    list_display = ('place', 'type')
    list_filter = ('type',)


class AnswerAdmin(admin.ModelAdmin):

    def is_correct(self, a):
        return a.place_answered == a.place_asked
    is_correct.short_description = 'Correct'
    is_correct.boolean = True

    def asked_ago(self, a):
        return pretty_date(a.inserted)
    asked_ago.short_description = 'When Asked'

    list_display = (
        'user',
        'type',
        'number_of_options',
        'place_asked',
        'place_answered',
        'is_correct',
        'asked_ago')
    search_fields = ('user__username', 'place_asked__code', 'place_asked__name',)
    actions = [export_selected_objects]


class PriorSkillAdmin(admin.ModelAdmin):
    list_display = ('user', 'value')


class CurrentSkillAdmin(admin.ModelAdmin):
    list_display = ('place', 'user', 'value')


class DifficultyAdmin(admin.ModelAdmin):
    list_display = ('place', 'value')

################################################################################
# registers

admin.site.register(Answer, AnswerAdmin)
admin.site.register(Place, PlaceAdmin)
admin.site.register(PlaceRelation, PlaceRelationAdmin)
admin.site.register(PriorSkill, PriorSkillAdmin)
admin.site.register(CurrentSkill, CurrentSkillAdmin)
admin.site.register(Difficulty, DifficultyAdmin)
