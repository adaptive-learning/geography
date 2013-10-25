from django.db import models


class PlaceManager(models.Manager):
    def get_continents(self):
        return self.filter(type=Place.CONTINENT)


class Place(models.Model):
    STATE = 1
    CITY = 2
    WORLD = 3
    CONTINENT = 4
    PLACE_TYPES = (
        (STATE, 'State'),
        (CITY, 'City'),
        (WORLD, 'World'),
        (CONTINENT, 'Continent'),
    )
    DIFFICULTY_CONVERSION = 1000000.0
    code = models.CharField(
        max_length=10,
        db_index=True,
        unique=True)  # TODO: change to SlugField
    name = models.CharField(max_length=100)
    difficulty = models.IntegerField(default=0)
    # TODO: change to PositiveSmallIntegerField
    type = models.IntegerField(choices=PLACE_TYPES)
    objects = PlaceManager()

    def __unicode__(self):
        return u'{0} ({1})'.format(self.name, self.code)

        self.save()

    def to_serializable(self):
        return {
            'code': self.code,
            'name': self.name
        }

    class Meta:
        ordering = ['type', 'name']


class PlaceRelationManager(models.Manager):

    def get_bordering_places(self, place):
        try:
            pr = self.get(place=place, type=PlaceRelation.HAVE_LAND_BORDER)
            prs = self.filter(
                related_places__in=pr.related_places.all(),
                type=PlaceRelation.HAVE_LAND_BORDER)
            return (
                Place.objects.exclude(id=place.id).filter(
                    id__in=[p.place_id for p in prs])
            )
        except PlaceRelation.DoesNotExist:
            return Place.objects.filter(code="###")


class PlaceRelation(models.Model):
    IS_ON_MAP = 1
    IS_SUBMAP = 2
    HAVE_LAND_BORDER = 3
    PLACE_RELATION_TYPES = (
        (IS_ON_MAP, 'Is On Map'),
        (IS_SUBMAP, 'Is Submap'),
        (HAVE_LAND_BORDER, 'Have Land Border'),
    )
    place = models.ForeignKey(
        Place,
        db_index=True,
        related_name='relation_place')
    related_places = models.ManyToManyField(Place)
    type = models.IntegerField(choices=PLACE_RELATION_TYPES, default=1)
    objects = PlaceRelationManager()
