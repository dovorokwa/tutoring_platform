from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.conf import settings  # Important for .env access
from .models import Subject, StudentProfile
from .forms import StudentRegistrationForm

def landing(request):
    """The public landing page for new clients."""
    return render(request, 'classes/landing.html')

def register(request):
    """Handles new student sign-ups and subject selection."""
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create the profile and link the chosen subjects
            profile = StudentProfile.objects.create(user=user)
            selected_subjects = form.cleaned_data.get('subjects')
            profile.enrolled_subjects.set(selected_subjects)
            profile.save()
            
            login(request, user)
            return redirect('dashboard')
    else:
        form = StudentRegistrationForm()
    return render(request, 'classes/register.html', {'form': form})

@login_required
def dashboard(request):
    """The protected area. Redirects to payment if unpaid."""
    # Get or create the user's profile
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    
    if not profile.has_paid:
        # Check how many subjects they picked during registration
        subjects = profile.enrolled_subjects.all()
        count = subjects.count()
        
        # Calculate dynamic price: R380 for 1, R700 for 2+
        price = 700 if count >= 2 else 380
        
        return render(request, 'classes/payment.html', {
            'price': price,
            'subjects': subjects,
            'PAYSTACK_PUBLIC_KEY': settings.PAYSTACK_PUBLIC_KEY  # From .env via settings.py
        })
    
    # If they have paid, show the dashboard with links and schedule
    subjects = profile.enrolled_subjects.all()
    return render(request, 'classes/dashboard.html', {'subjects': subjects})

@login_required
def payment_success(request):
    """Updates the database once Paystack confirms success."""
    profile = StudentProfile.objects.get(user=request.user)
    profile.has_paid = True
    
    # Optional: Save the reference sent from the frontend
    ref = request.GET.get('ref')
    if ref:
        profile.paystack_ref = ref
        
    profile.save()
    return redirect('dashboard')