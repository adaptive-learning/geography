from models import UserProfile
from django.contrib import admin


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'send_emails')


admin.site.register(UserProfile, UserProfileAdmin)
