# /root/tutoring_platform/classes/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Subject, StudentProfile

class StudentRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)

    grade = forms.ChoiceField(choices=[(i, f"Grade {i}") for i in range(8, 13)])
    
    # We change this to a MultipleChoiceField so we can manually define choices
    subjects = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super(StudentRegistrationForm, self).__init__(*args, **kwargs)
        
        # Manually create unique choices based on name to avoid .distinct() errors
        all_subjects = Subject.objects.all()
        unique_names = sorted(list(set(s.name for s in all_subjects)))
        self.fields['subjects'].choices = [(name, name) for name in unique_names]

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password'])
        user.is_active = False 
        if commit:
            user.save()
        return user