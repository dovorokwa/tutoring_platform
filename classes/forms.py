from django import forms
from django.contrib.auth.models import User
from .models import Subject, StudentProfile

class StudentRegistrationForm(forms.ModelForm):
    # Custom fields for Name and Phone
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-input'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Surname', 'class': 'form-input'})
    )
    phone_number = forms.CharField(
        max_length=15, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Cell Phone Number', 'class': 'form-input'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email Address', 'class': 'form-input'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Create Password', 'class': 'form-input'})
    )

    grade = forms.ChoiceField(
        choices=[(i, f"Grade {i}") for i in range(8, 13)],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.none(), 
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super(StudentRegistrationForm, self).__init__(*args, **kwargs)
        # FIX: SQLite-friendly way to get unique subject names
        # We fetch all subjects, but in the view logic we map them to the specific grade
        self.fields['subjects'].queryset = Subject.objects.all().order_by('name')

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        # Email becomes the username
        user.username = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password'])
        
        # Inactive until email verification
        user.is_active = False 
        
        if commit:
            user.save()
        return user