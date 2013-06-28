from django.db import models
from django.contrib.auth.models import User
from datetime import datetime   

class Place(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    difficulty = models.IntegerField(default=0)
    def __unicode__(self):
        return u'{} ({})'.format(self.name, self.code)

class Student(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    points = models.IntegerField(default=0)
    skill = models.IntegerField(default=0)
    def __unicode__(self):
        return self.user.username
    @staticmethod
    def fromUser(user):
        try:
            user = User.objects.get(username = user.username)
            student = Student.objects.get(user = user)
        except User.DoesNotExist:
            student = None
        except Student.DoesNotExist:
            student = Student(user=user)
            student.save()
        return student
    

class UsersPlace(models.Model):
    user = models.ForeignKey(Student)
    place = models.ForeignKey(Place)
    askedCount = models.IntegerField(default=0)
    correctlyAnsweredCount = models.IntegerField(default=0)
    lastAsked = models.DateTimeField(default=datetime.now)
    @staticmethod
    def fromStudentAndPlace(student, place):
        try:
            usersPlace = UsersPlace.objects.get(user = student, place = place)
        except UsersPlace.DoesNotExist:
            usersPlace = UsersPlace(
                user = student, 
                place = place,
            )
        return usersPlace 
    def __unicode__(self):
        return u'user: {}, place: {}'.format( self.user, self.place)

class Answer(models.Model):
    user = models.ForeignKey(Student)
    place = models.ForeignKey(Place, related_name='place_id')
    answer = models.ForeignKey(Place, related_name='answer_id', null=True, blank=True, default = None)
    type = models.IntegerField()
    askedDate = models.DateTimeField(default=datetime.now)
    msResposeTime = models.IntegerField(default=0)
    def __unicode__(self):
        return u'user: {}, requested: {}, answered: {}, correct: {}'.format( self.user, self.place, self.answer, self.place == self.answer)
