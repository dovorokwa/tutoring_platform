from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Subject, StudentProfile
from .forms import StudentRegistrationForm

def landing(request):
    """The public landing page."""
    return render(request, 'classes/landing.html')

def register(request):
    """Handles new student sign-ups and subject selection."""
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create profile and attach subjects
            profile = StudentProfile.objects.create(user=user)
            selected_subjects = form.cleaned_data.get('subjects')
            profile.enrolled_subjects.set(selected_subjects)
            profile.save()
            
            login(request, user)
            # Pass a flag so the dashboard knows NOT to say "Welcome Back" yet
            return redirect('dashboard')
    else:
        form = StudentRegistrationForm()
    return render(request, 'classes/register.html', {'form': form})

@login_required
def dashboard(request):
    """
    The gatekeeper view. 
    If unpaid: redirects to payment summary.
    If paid: shows MS Teams links.
    """
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    
    if not profile.has_paid:
        subjects = profile.enrolled_subjects.all()
        
        # If a student has no subjects, they shouldn't be here
        if not subjects.exists():
            return render(request, 'classes/payment.html', {
                'error': 'No subjects selected. Please contact support.',
                'price': 0
            })

        # Logic for R380 vs R700
        count = subjects.count()
        price = 700 if count >= 2 else 380
        
        # Logic to determine if we show the "Welcome Back" alert
        # We show it if they have been registered for more than 1 minute 
        # (meaning they didn't JUST come from the register page)
        from django.utils import timezone
        is_returning = (timezone.now() - request.user.date_joined).total_seconds() > 60

        return render(request, 'classes/payment.html', {
            'price': price,
            'subjects': subjects,
            'PAYSTACK_PUBLIC_KEY': settings.PAYSTACK_PUBLIC_KEY,
            'is_returning': is_returning  
        })
    
    # SUCCESS: User has paid, show the actual class links
    return render(request, 'classes/dashboard.html', {
        'subjects': profile.enrolled_subjects.all()
    })

@login_required
def payment_success(request):
    """Unlocks account and saves Paystack reference."""
    profile = StudentProfile.objects.get(user=request.user)
    
    ref = request.GET.get('ref')
    if ref:
        profile.paystack_ref = ref
    
    profile.has_paid = True
    profile.save()
    
    return redirect('dashboard')