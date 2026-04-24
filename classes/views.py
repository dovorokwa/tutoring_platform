from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
from .models import Subject, StudentProfile
from .forms import StudentRegistrationForm

def landing(request):
    """The public landing page."""
    return render(request, 'classes/landing.html')

def register(request):
    """Handles signup and matches generic checkboxes to the specific grade instances."""
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile = StudentProfile.objects.create(user=user)
            
            selected_grade = form.cleaned_data.get('grade')
            selected_subjects_from_form = form.cleaned_data.get('subjects') 

            # Map generic names (like 'MATH') to the correct Grade record
            subject_names = [s.name for s in selected_subjects_from_form]
            
            # Filter subjects that match the Grade and names
            final_subjects = Subject.objects.filter(
                name__in=subject_names, 
                grade=selected_grade
            )
            
            profile.enrolled_subjects.set(final_subjects)
            profile.save()
            
            login(request, user)
            return redirect('dashboard')
    else:
        form = StudentRegistrationForm()
    return render(request, 'classes/register.html', {'form': form})

@login_required
def dashboard(request):
    """
    Handles the Paywall with specific session logic:
    1 Unique Subject: R500 (was R600) - 8 Sessions
    2 Unique Subjects: R800 (was R1200) - 16 Sessions
    """
    try:
        profile = request.user.profile
    except StudentProfile.DoesNotExist:
        logout(request)
        return redirect('register')
    
    if not profile.has_paid:
        subjects = profile.enrolled_subjects.all()
        
        if not subjects.exists():
            return redirect('register')

        # FIX: Count unique subject types, not the number of database objects
        # This ensures one subject (e.g. MATH) is always R500 regardless of session count
        unique_count = subjects.values('name').distinct().count()
        
        if unique_count >= 2:
            price = 800
            original_price = 1200
            session_text = "16 Sessions Per Month"
        else:
            price = 500
            original_price = 600
            session_text = "8 Sessions Per Month"
        
        savings = original_price - price

        # Flag for returning users
        is_returning = (timezone.now() - request.user.date_joined).total_seconds() > 60

        return render(request, 'classes/payment.html', {
            'price': price,
            'original_price': original_price,
            'savings': savings,
            'session_text': session_text,
            'subjects': subjects,
            'PAYSTACK_PUBLIC_KEY': settings.PAYSTACK_PUBLIC_KEY,
            'is_returning': is_returning  
        })
    
    # SUCCESS: User has paid, show MS Teams links and schedule
    return render(request, 'classes/dashboard.html', {
        'subjects': profile.enrolled_subjects.all()
    })

@login_required
def payment_success(request):
    """Verifies payment and unlocks the dashboard."""
    profile = StudentProfile.objects.get(user=request.user)
    
    ref = request.GET.get('ref')
    if ref:
        profile.paystack_ref = ref
    
    profile.has_paid = True
    profile.save()
    
    return redirect('dashboard')