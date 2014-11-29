from models import Rating
from django.contrib import admin


class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'value', 'inserted')


admin.site.register(Rating, RatingAdmin)
