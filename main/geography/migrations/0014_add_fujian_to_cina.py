# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from geography.models import Place, PlaceRelation


class Migration(DataMigration):

    dependencies = [("migrations", "0013_remove_geneva_from_europe")]

    def forwards(self, orm):
        cina = PlaceRelation.objects.get(place__code="cn", type=PlaceRelation.IS_ON_MAP)
        fujian = Place.objects.get(code="CN-")
        fujian.code = "cn-35"
        fujian.save()
        cina.related_places.add(fujian)
        cina.save()

    def backwards(self, orm):
        cina = PlaceRelation.objects.get(place__code="cn", type=PlaceRelation.IS_ON_MAP)
        fujian = Place.objects.get(code="cn-35")
        fujian.code = "CN-"
        fujian.save()
        cina.related_places.remove(fujian)
        cina.save()

    complete_apps = ['geography']
