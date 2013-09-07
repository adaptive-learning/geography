from django.db import models
from datetime import datetime, timedelta
from core.models import Place, PlaceRelation
from accounts.models import Student

# Create your models here.

def yesterday():
    y = datetime.now() - timedelta(days=1)
    return y

class UsersPlaceManager(models.Manager):
    def fromStudentAndPlace(self, student, place):
        try:
            usersPlace = UsersPlace.objects.get(user=student, place=place)
        except UsersPlace.DoesNotExist:
            usersPlace = UsersPlace(
                user=student,
                place=place,
            )
        return usersPlace 

    def addAnswer(self, a):
        usersPlace = self.fromStudentAndPlace(a.user, a.place)
        usersPlace._addAnswer(a)

def all_correct(users_places):
    incorrect =  [up for up in users_places if up.skill < 1]
    return len(incorrect) == 0

def updatePlaceDifficulty(place):
    usersPlaces = UsersPlace.objects.filter(place=place)
    skills = [ up.correctlyAnsweredCount / float(up.askedCount) for up in usersPlaces]
    difficulty = sum(skills) / len(skills) if len(skills) > 0 else 0.5
    place.difficulty = int((1 - difficulty) * Place.DIFFICULTY_CONVERSION)

class UsersPlace(models.Model):
    user = models.ForeignKey(Student)
    place = models.ForeignKey(Place)
    askedCount = models.IntegerField(default=0)
    skill = models.FloatField(default=0)
    correctlyAnsweredCount = models.IntegerField(default=0)
    lastAsked = models.DateTimeField(default=yesterday)
    first_asked = models.DateTimeField(default=datetime.now)
    objects = UsersPlaceManager()
    
    def similar_places_knowladge(self):
        map = PlaceRelation.objects.filter(related_places=self.place, type=PlaceRelation.IS_ON_MAP)[0]
        last_users_places = UsersPlace.objects.filter(
                 user=self.user,
                 place_id__in=map.related_places.all(), 
#                  lastAsked__lt=min(self.lastAsked, datetime.now())
        ).order_by("-lastAsked")[:10]
        correct =  [up for up in last_users_places if up.skill == 1]
        if len(last_users_places) < 5:
            return 0
        knowladge = 1.0*len(correct) / len(last_users_places)
#         raise Exception(u"similar {0} {1}".format(knowladge, self.place.name))
        return knowladge
    
    def get_skill(self):
        skill = self.correctlyAnsweredCount / float(self.askedCount) if self.askedCount > 0 else 0
        skill = round(skill, 2)
        return skill
    
    def certainty(self):
        # TODO: create a field instead of this method
        newCertainty = self.askedCount / 3.0
#         raise Exception(u"here {0}".format(similar_places_knowladge(self.place)))
        if self.askedCount <= 2 and self.correctlyAnsweredCount == self.askedCount:
            if self.similar_places_knowladge() >= 0.9:
                newCertainty = 1
        notSeenFor = datetime.now() - max(self.lastAsked, datetime.now()) 
        knownFor = self.lastAsked - self.first_asked
        if float(notSeenFor.days) > 0:
            notSeenForRatio = min(1, 0.9 * knownFor.days / float(notSeenFor.days))
        else:
            notSeenForRatio = 1
        certainty = min(newCertainty, notSeenForRatio)
        certainty = round(certainty, 2)
        return certainty

    def _addAnswer(self, a):
        self.askedCount += 1
        if (a.place == a.answer):
            self.correctlyAnsweredCount += 1
            self.lastAsked = datetime.now()
        self.skill = self.get_skill()
        self.save()
        updatePlaceDifficulty(self.place)

    def __unicode__(self):
        return u'user: {0}, place: [{1}]'.format(self.user, self.place)
    
    def to_serializable(self):
        ret = self.place.to_serializable()
        ret.update({
          'skill' : self.skill,
          'certainty' : self.certainty(),
        })
        return ret
    class Meta:
        db_table = 'core_usersplace' #TODO migrate lagacy db_table
    

class Answer(models.Model):
    user = models.ForeignKey(Student)
    place = models.ForeignKey(Place, related_name='place_id')
    answer = models.ForeignKey(Place, related_name='answer_id', null=True, blank=True, default=None)
    type = models.IntegerField() # TODO: change to PositiveSmallIntegerField
    askedDate = models.DateTimeField(default=datetime.now)
    msResposeTime = models.IntegerField(default=0)
    # TODO: options = models.ManyToManyField(Place)
    
#     def get_no_of_options(self):
#         qt = get_question_type_by_id(self.type)
#         no_of_options =  qt.no_of_options
#         if no_of_options == 0:
#             no_of_options = Map.objects.get(places=self.place).places.all().count()
#         return no_of_options
#     
    def __unicode__(self):
        return u'user: {0}, requested: {1}, answered: {2}, correct: {3}'.format(self.user, self.place, self.answer, self.place == self.answer)
    class Meta:
        ordering = ["-askedDate"]
        db_table = 'core_answer' #TODO migrate lagacy db_table


class ConfusedPlacesManager(models.Manager):
    def was_confused(self, askedPlace, answeredPlace):
        if answeredPlace == None:
            return
        try:
            confused = self.get(asked=askedPlace, confused_with=answeredPlace)
        except ConfusedPlaces.DoesNotExist:
            confused = ConfusedPlaces(
                  asked=askedPlace,
                  confused_with=answeredPlace,
            )
        confused.level_of_cofusion += 1
        confused.save()

    def get_similar_to(self, place):
        return [c.confused_with for c in self.filter(asked=place)]

class ConfusedPlaces(models.Model):
    asked = models.ForeignKey(Place, related_name='asked_id')
    confused_with = models.ForeignKey(Place, related_name='confused_with_id')
    level_of_cofusion = models.IntegerField(default=0)
    objects = ConfusedPlacesManager()
    class Meta:
        ordering = ["-level_of_cofusion"]
        db_table = 'core_confusedplaces' #TODO migrate lagacy db_table



