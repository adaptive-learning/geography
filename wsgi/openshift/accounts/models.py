from django.db import models
from django.contrib.auth.models import User

# Create your models here.


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
            'username': self.user.username,
            'points': self.points,
        }

    class Meta:
        db_table = 'core_student'  # TODO migrate lagacy db_table
