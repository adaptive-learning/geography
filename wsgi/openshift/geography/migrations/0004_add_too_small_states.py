# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from geography.models import Place, PlaceRelation, UserPlace


class Migration(DataMigration):

    dependencies = [("migrations", "0003_regions_translate")]

    def forwards(self, orm):

        world_states = PlaceRelation.objects.get(
            place__code="world",
            type=PlaceRelation.IS_ON_MAP
        ).related_places.all()
        india_states = PlaceRelation.objects.get(
            place__code="in",
            type=PlaceRelation.IS_ON_MAP
        ).related_places.all()
        us_states = PlaceRelation.objects.get(
            place__code="us",
            type=PlaceRelation.IS_ON_MAP
        ).related_places.all()

        small_states = Place.objects.filter(
            type=Place.STATE
        ).exclude(
            id__in=world_states | india_states | us_states,
            code__in=["Andaman and Nicobar",
                      "Chandigarh",
                      "Dadra and Nagar Haveli",
                      "Daman and Diu",
                      "Delhi",
                      "Lakshadweep",
                      "Puducherry"]
        )

        world = Place.objects.get(code="world")
        pr = PlaceRelation(place=world, type=PlaceRelation.IS_TOO_SMALL_ON_MAP)
        pr.save()
        pr.related_places = small_states
        pr.save()

    def backwards(self, orm):
        pass

    complete_apps = ['geography']
