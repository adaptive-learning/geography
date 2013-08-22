from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Min


class Place(models.Model):
    DIFFICULTY_CONVERSION = 1000000.0
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    difficulty = models.IntegerField(default=0)
    def __unicode__(self):
        return u'{0} ({1}) difficulty: {2}'.format(self.name, self.code, self.difficulty / Place.DIFFICULTY_CONVERSION)
    
    def updateDifficulty(self):
        usersPlaces = UsersPlace.objects.filter(place=self)
        skills = [ up.correctlyAnsweredCount / float(up.askedCount) for up in usersPlaces]
        difficulty = sum(skills) / len(skills) if len(skills) > 0 else 0.5
        self.difficulty = int((1 - difficulty) * Place.DIFFICULTY_CONVERSION)
        self.save()
    def to_serializable(self):
        return {
          'code' : self.code,
          'name' : self.name
        }

class StudentManager(models.Manager):
    def fromUser(self, user):
        try:
            user = User.objects.get(username=user.username)
            student = self.get(user=user)
        except User.DoesNotExist:
            student = None
        except Student.DoesNotExist:
            student = Student(user=user)
            student.save()
        return student
    

class Student(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    points = models.IntegerField(default=0)
    skill = models.IntegerField(default=0)
    objects = StudentManager()
    
    def __unicode__(self):
        return self.user.username

    def to_serializable(self):
        return {
            'username' : self.user.username,
            'points' :  self.points,
        }

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

class UsersPlace(models.Model):
    user = models.ForeignKey(Student)
    place = models.ForeignKey(Place)
    askedCount = models.IntegerField(default=0)
    correctlyAnsweredCount = models.IntegerField(default=0)
    lastAsked = models.DateTimeField(default=yesterday)
    objects = UsersPlaceManager()
    
    def skill(self):
        skill = self.correctlyAnsweredCount / float(self.askedCount) if self.askedCount > 0 else 0
        skill = round(skill, 2)
        return skill
    
    def certainty(self):
        newCertainty = self.askedCount / 3.0
        notSeenFor = datetime.now() - max(self.lastAsked, datetime.now()) 
        knownFor = self.lastAsked - self.firstAsked() if self.firstAsked() != None else timedelta()
        if (float(notSeenFor.days) > 0):
            notSeenForRatio = min(1, 0.9 * knownFor.days / float(notSeenFor.days))
        else:
            notSeenForRatio = 1
        certainty = min(newCertainty, notSeenForRatio)
        certainty = round(certainty, 2)
        return certainty
    
    def firstAsked(self):
        return Answer.objects.filter(
              user=self.user,
              place=self.place
          ).aggregate(Min('askedDate'))['askedDate__min']

    def _addAnswer(self, a):
        self.askedCount += 1
        if (a.place == a.answer):
            self.correctlyAnsweredCount += 1
            self.lastAsked = datetime.now()
        self.save()
        self.place.updateDifficulty()

    def __unicode__(self):
        return u'user: {0}, place: [{1}]'.format(self.user, self.place)
    
    def to_serializable(self):
        ret = self.place.to_serializable()
        ret.update({
          'skill' : self.skill(),
          'certainty' : self.certainty(),
        })
        return ret
    

class Answer(models.Model):
    user = models.ForeignKey(Student)
    place = models.ForeignKey(Place, related_name='place_id')
    answer = models.ForeignKey(Place, related_name='answer_id', null=True, blank=True, default=None)
    type = models.IntegerField()
    askedDate = models.DateTimeField(default=datetime.now)
    msResposeTime = models.IntegerField(default=0)
    
    def __unicode__(self):
        return u'user: {0}, requested: {1}, answered: {2}, correct: {3}'.format(self.user, self.place, self.answer, self.place == self.answer)
    class Meta:
        ordering = ["-askedDate"]


class Map(models.Model):
    name = models.CharField(max_length=100)
    places = models.ManyToManyField(Place)
    def __unicode__(self):
        return u'Map: {0}'.format(self.name)

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
