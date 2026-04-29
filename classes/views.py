from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.contrib.auth.models import User

from .models import Subject, StudentProfile
from .forms import StudentRegistrationForm, ContactForm 

def landing(request):
    """The public landing page."""
    return render(request, 'classes/landing.html')

def register(request):
    """Handles signup, sends verification email, and saves phone/subjects."""
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            # 1. Save user (is_active will be False from forms.py logic)
            user = form.save()
            
            # 2. Update Profile with phone number and subjects
            profile, created = StudentProfile.objects.get_or_create(user=user)
            profile.phone_number = form.cleaned_data.get('phone_number')
            
            selected_grade = form.cleaned_data.get('grade')
            selected_subjects_from_form = form.cleaned_data.get('subjects') 
            subject_names = [s.name for s in selected_subjects_from_form]
            
            final_subjects = Subject.objects.filter(
                name__in=subject_names, 
                grade=selected_grade
            )
            profile.enrolled_subjects.set(final_subjects)
            profile.save()

            # 3. Send Verification Email
            current_site = get_current_site(request)
            mail_subject = 'Verify your MyTutor CAPS Account'
            message = render_to_string('classes/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            
            try:
                email.send()
                # Show success page telling them to check their inbox
                return render(request, 'classes/verification_sent.html', {'email': to_email})
            except Exception as e:
                messages.error(request, f"Error sending email: {e}. Please check your settings.")
                return redirect('register')
    else:
        form = StudentRegistrationForm()
    return render(request, 'classes/register.html', {'form': form})

def activate(request, uidb64, token):
    """View that handles clicking the link in the email."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        profile = user.profile
        profile.is_email_verified = True
        profile.save()
        
        login(request, user)
        messages.success(request, 'Email verified! You can now finalize your enrollment.')
        return redirect('dashboard')
    else:
        return render(request, 'classes/activation_invalid.html')

@login_required
def dashboard(request):
    """Handles the Paywall and Session Logic."""
    try:
        profile = request.user.profile
    except StudentProfile.DoesNotExist:
        profile = StudentProfile.objects.create(user=request.user)
    
    if not profile.has_paid:
        subjects = profile.enrolled_subjects.all()
        
        if not subjects.exists():
            # If user has no subjects, they need to select them
            return redirect('register')

        unique_count = subjects.values('name').distinct().count()
        
        if unique_count >= 2:
            price, original_price = 800, 1200
            session_text = "16 Sessions Per Month"
        else:
            price, original_price = 500, 600
            session_text = "8 Sessions Per Month"
        
        savings = original_price - price
        is_returning = (timezone.now() - request.user.date_joined).total_seconds() > 60
        paystack_key = getattr(settings, 'PAYSTACK_PUBLIC_KEY', None)

        return render(request, 'classes/payment.html', {
            'price': price,
            'original_price': original_price,
            'savings': savings,
            'session_text': session_text,
            'subjects': subjects,
            'PAYSTACK_PUBLIC_KEY': paystack_key,
            'is_returning': is_returning  
        })
    
    return render(request, 'classes/dashboard.html', {
        'subjects': profile.enrolled_subjects.all()
    })

@login_required
def payment_success(request):
    profile = request.user.profile
    ref = request.GET.get('ref')
    
    if ref:
        profile.paystack_ref = ref
        profile.has_paid = True
        profile.save()
        messages.success(request, "Payment successful! Welcome to your dashboard.")
        return redirect('dashboard')
    
    messages.error(request, "Payment verification failed.")
    return redirect('dashboard')

def tutor_profiles(request):
    return render(request, 'classes/tutors.html')

def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your message has been sent!")
            return redirect('contact_us')
    else:
        form = ContactForm()
    return render(request, 'classes/contact.html', {'form': form})