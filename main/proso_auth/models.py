from django.contrib.auth.models import User
from django.db import models


class UserProfileManager(models.Manager):
    def get_profile(self, user):
        try:
            profile = self.get(user=user)
        except UserProfile.DoesNotExist:
            profile = UserProfile(user=user)
            profile.save()
        return profile


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    send_emails = models.BooleanField(default=True)
    objects = UserProfileManager()

    class Meta:
        app_label = 'geography'
