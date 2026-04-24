from django.db import models
from django.contrib.auth.models import User

class Subject(models.Model):
    SUBJECT_CHOICES = [
        ('MATH', 'Mathematics'), 
        ('PHYS', 'Physical Science')
    ]
    
    GRADE_CHOICES = [(i, f'Grade {i}') for i in range(8, 13)]

    DAY_CHOICES = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
    ]
    
    name = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    grade = models.IntegerField(choices=GRADE_CHOICES)
    
    # New Fields for the Dashboard Schedule
    day = models.CharField(max_length=3, choices=DAY_CHOICES, default='MON')
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # Links
    teams_link = models.URLField(max_length=500)
    whatsapp_link = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.get_name_display()} - Grade {self.grade} ({self.get_day_display()})"

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    has_paid = models.BooleanField(default=False)
    enrolled_subjects = models.ManyToManyField(Subject, blank=True)
    
    # To track Paystack transactions
    paystack_ref = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"