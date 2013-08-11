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
    def toSerializable(self):
        return {
          'code' : self.code,
          'name' : self.name
        }


class Student(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    points = models.IntegerField(default=0)
    skill = models.IntegerField(default=0)
    def __unicode__(self):
        return self.user.username
    @staticmethod
    def fromUser(user):
        try:
            user = User.objects.get(username=user.username)
            student = Student.objects.get(user=user)
        except User.DoesNotExist:
            student = None
        except Student.DoesNotExist:
            student = Student(user=user)
            student.save()
        return student
    
    def toSerializable(self):
        return {
            'username' : self.user.username,
            'points' :  self.points,
        }

def yesterday():
    y = datetime.now() - timedelta(days=1)
    return y

class UsersPlace(models.Model):
    user = models.ForeignKey(Student)
    place = models.ForeignKey(Place)
    askedCount = models.IntegerField(default=0)
    correctlyAnsweredCount = models.IntegerField(default=0)
    lastAsked = models.DateTimeField(default=yesterday)
    def skill(self):
        skill = self.correctlyAnsweredCount / float(self.askedCount)
        skill = round(skill, 2)
        return skill
    
    def certainty(self):
        newCertainty = self.askedCount / 3.0
        notSeenFor = datetime.now() - self.lastAsked
        knownFor = self.lastAsked - self.firstAsked()
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

    @staticmethod
    def fromStudentAndPlace(student, place):
        try:
            usersPlace = UsersPlace.objects.get(user=student, place=place)
        except UsersPlace.DoesNotExist:
            usersPlace = UsersPlace(
                user=student,
                place=place,
            )
        return usersPlace 

    @staticmethod
    def addAnswer(a):
        usersPlace = UsersPlace.fromStudentAndPlace(a.user, a.place)
        usersPlace._addAnswer(a)

    def _addAnswer(self, a):
        self.askedCount += 1
        if (a.place == a.answer):
            self.correctlyAnsweredCount += 1
            self.lastAsked = datetime.now()
        self.save()
        self.place.updateDifficulty()

    def __unicode__(self):
        return u'user: {0}, place: [{1}]'.format(self.user, self.place)
    
    def toSerializable(self):
        ret = self.place.toSerializable()
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

