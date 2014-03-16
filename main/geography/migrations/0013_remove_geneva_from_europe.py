# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from geography.models import Place, PlaceRelation


class Migration(DataMigration):

    dependencies = [("migrations", "0012_fix_codes_of_de_and_in")]

    def forwards(self, orm):
        europe = PlaceRelation.objects.get(place__code="europe")
        geneva = Place.objects.get(code="Geneva")
        europe.related_places.remove(geneva)
        europe.save()

    def backwards(self, orm):
        europe = PlaceRelation.objects.get(place__code="europe")
        geneva = Place.objects.get(code="Geneva")
        europe.related_places.add(geneva)
        europe.save()

    complete_apps = ['geography']
