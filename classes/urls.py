from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('tutors/', views.tutor_profiles, name='tutor_profiles'),
]