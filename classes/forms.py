from django import forms
from django.contrib.auth.models import User
from .models import Subject

class StudentRegistrationForm(forms.ModelForm):
    # 1. Grade selection dropdown
    grade = forms.ChoiceField(
        choices=[('', 'Select Your Grade')] + [(i, f'Grade {i}') for i in range(8, 13)],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none transition bg-white',
        }),
        required=True
    )

    # 2. Password field
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none transition',
        'placeholder': 'Create a secure password'
    }))

    # 3. Subject selection checkboxes (Generic List)
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.none(),
        widget=forms.CheckboxSelectMultiple(),
        required=True,
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        unique_ids = []
        seen_names = set()
        
        for subject in Subject.objects.all():
            if subject.name not in seen_names:
                unique_ids.append(subject.id)
                seen_names.add(subject.name)
        
        self.fields['subjects'].queryset = Subject.objects.filter(id__in=unique_ids)
        self.fields['subjects'].label_from_instance = lambda obj: f"{obj.get_name_display()}"

    # --- VALIDATION METHODS ---

    def clean_username(self):
        """Checks if the username is already taken."""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username already exists. Please login.")
        return username

    def clean_email(self):
        """Checks if the email is already in use."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists. Please login.")
        return email

    # --- SAVE METHOD ---

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user