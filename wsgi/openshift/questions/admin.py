from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from questions.models import Answer, UsersPlace, ConfusedPlaces


def export_selected_objects(modeladmin, request, queryset):
    selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
    ct = ContentType.objects.get_for_model(queryset.model)
    return (
        HttpResponseRedirect(
            "/export/?model=%s.%s&ids=%s" %
            (ct.app_label, ct.model, ",".join(selected)))
    )


class UsersPlaceAdmin(admin.ModelAdmin):

    def first_asked_ago(self, a):
        return pretty_date(a.first_asked)
    first_asked_ago.short_description = 'First Asked'

    def last_asked_ago(self, a):
        return pretty_date(a.lastAsked)
    last_asked_ago.short_description = 'Last Asked'

    list_display = (
        'user',
        'place',
        'skill',
        'first_asked_ago',
        'last_asked_ago')
    search_fields = ('user__user__username', 'place__code', 'place__name', )


class AnswerAdmin(admin.ModelAdmin):

    def is_correct(self, a):
        return a.place == a.answer
    is_correct.short_description = 'Correct'
    is_correct.boolean = True

    def asked_ago(self, a):
        return pretty_date(a.askedDate)
    asked_ago.short_description = 'When Asked'

    list_display = (
        'user',
        'type',
        'place',
        'answer',
        'is_correct',
        'asked_ago')
    search_fields = ('user__user__username', 'place__code', 'place__name', )
    actions = [export_selected_objects]


class ConfusedPlacesAdmin(admin.ModelAdmin):
    list_display = ('asked', 'confused_with', 'level_of_cofusion')

admin.site.register(UsersPlace, UsersPlaceAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(ConfusedPlaces, ConfusedPlacesAdmin)


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
