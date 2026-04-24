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
        
        # This logic ensures the user ONLY sees "Mathematics" and "Physical Science" once.
        # This prevents the "Double Math" charging error.
        unique_ids = []
        seen_names = set()
        
        # We loop through all subjects and grab ONLY the first ID for each name
        # (e.g., if it finds Grade 8 Maths first, it takes that ID and skips all other Maths)
        for subject in Subject.objects.all():
            if subject.name not in seen_names:
                unique_ids.append(subject.id)
                seen_names.add(subject.name)
        
        # Update the checkboxes to only show these unique entries
        self.fields['subjects'].queryset = Subject.objects.filter(id__in=unique_ids)
        
        # Display clean labels (e.g., "Mathematics") without the Grade attached
        self.fields['subjects'].label_from_instance = lambda obj: f"{obj.get_name_display()}"

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user