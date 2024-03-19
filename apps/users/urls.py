from django.urls import path
from .views.register import *

urlpatterns = [
    path('auth/verify', Verification.as_view(), name="verification"),

    path('register/steps/account_type', RegistrationAccountType.as_view(), name='register_account_type'),
    path('register/steps/phone_number', RegistrationPhoneNumber.as_view(), name='register_phone_number'),
    path('register/steps/profile_name', RegistrationProfileName.as_view(), name='register_profile_name'),
    path('register/steps/profile_metadata', RegistrationProfileMetadata.as_view(), name='register_profile_metadata'),
    path('register/steps/email', RegistrationEmail.as_view(), name='register_email'),
    path('register/steps/parent_email', RegistrationParentEmail.as_view(), name='register_parent_email'),
    path('register/steps/password', RegistrationPassword.as_view(), name='register_password'),
    path('register', Registration.as_view(), name='register')
]
