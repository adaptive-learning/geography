from accounts.models import Student
from django.contrib import admin

class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'skill')
    
admin.site.register(Student, StudentAdmin)