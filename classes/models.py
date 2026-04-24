from django.db import models
from django.contrib.auth.models import User

class Subject(models.Model):
    SUBJECT_CHOICES = [
        ('MATH', 'Mathematics'), 
        ('PHYS', 'Physical Science')
    ]
    
    # Using choices for grade to make the Admin dropdown cleaner
    GRADE_CHOICES = [(i, f'Grade {i}') for i in range(8, 13)]
    
    name = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    grade = models.IntegerField(choices=GRADE_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    teams_link = models.URLField(max_length=500)
    whatsapp_link = models.URLField(max_length=500)

    def __str__(self):
        # We use str() here to ensure it always returns a string safely
        return f"{self.get_name_display()} - Grade {self.grade}"

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    has_paid = models.BooleanField(default=False)
    enrolled_subjects = models.ManyToManyField(Subject, blank=True)
    paystack_ref = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        # Using f-string ensures we don't get a "NoneType" error if the username is blank
        return f"{self.user.username}'s Profile"