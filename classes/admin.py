from django.contrib import admin
from .models import Subject, StudentProfile

# Clear and explicit registration
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'start_time', 'end_time')
    list_filter = ('grade', 'name')

class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'has_paid')
    list_filter = ('has_paid',)
    search_fields = ('user__username', 'user__email')

admin.site.register(Subject, SubjectAdmin)
admin.site.register(StudentProfile, StudentProfileAdmin)