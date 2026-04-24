from django import forms
from django.contrib.auth.models import User
from .models import Subject

class StudentRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none transition',
        'placeholder': 'Create a secure password'
    }))
    
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        help_text="Tick the subjects you want to attend."
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none transition',
                'placeholder': 'Choose a username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none transition',
                'placeholder': 'Enter your email address'
            }),
        }

    # --- THIS PART IS THE KEY TO FIXING YOUR LOGIN ISSUE ---
    def save(self, commit=True):
        user = super().save(commit=False)
        # set_password hashes the password so Django can recognize it during login
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user