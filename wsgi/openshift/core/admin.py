from core.models import Place, PlaceRelation
from django.contrib import admin

class PlaceAdmin(admin.ModelAdmin):
#     list_display = ('name', 'code', 'type', 'difficulty')
    list_display = ('name', 'code', 'difficulty')
    
class PlaceRelationAdmin(admin.ModelAdmin):
    list_display = ('place', 'type')
    
admin.site.register(Place, PlaceAdmin)
admin.site.register(PlaceRelation, PlaceRelationAdmin)
