from core.models import Place, PlaceRelation
from django.contrib import admin


class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'type', 'difficulty')
    list_filter = ('type', )


class PlaceRelationAdmin(admin.ModelAdmin):
    list_display = ('place', 'type')
    list_filter = ('type', )

admin.site.register(Place, PlaceAdmin)
admin.site.register(PlaceRelation, PlaceRelationAdmin)
