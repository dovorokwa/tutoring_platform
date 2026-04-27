from django.contrib import admin
from .models import Subject, StudentProfile
from .models import ContactMessage

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

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    # This makes the list view look professional and organized
    list_display = ('name', 'email', 'subject', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'subject')
    readonly_fields = ('created_at',) # Prevents changing the timestamp