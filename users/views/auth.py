from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from users.serializers.jwt import CustomTokenObtainPairSerializer
from users.serializers.auth import VerificationSerializer, RegistrationNameSerializer, \
    RegistrationBirthdayGenderSerializer, RegistrationTypeSerializer, RegistrationEmailSerializer, \
    RegistrationPasswordSerializer, RegistrationParentEmailSerializer

from users.utils.auth import generate_token, generate_verification_code, generate_unique_email_suggestions
from users.utils.functions import build_response
from users.tasks import send_sms, send_email

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated


class Verification(APIView):
    email_subject = _("Gozle ID Verification")
    email_text = _("Verification code: ")
    sms_text = _("Gozle ID verification code: ")

    def get_serializer_class(self, *args, **kwargs):
        return VerificationSerializer(*args, **kwargs)

    def post(self, request):
        token = request.data.get('token')

        serializer = VerificationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data.get("email")
            phone_number = serializer.validated_data.get("phone_number")

            if token:
                return build_response(
                    "success",
                    "Verification is complete",
                    status.HTTP_202_ACCEPTED
                )

            key, code = generate_verification_code(email, phone_number)
            cache.set(
                key,
                code,
                timeout=settings.VERIFICATION_CODE_TIMEOUT
            )

            if email and not phone_number:
                user_identifier = email
                send_email.delay(email, self.email_subject, self.email_text + str(code))
            else:
                user_identifier = phone_number
                send_sms.delay(phone_number.as_e164, self.sms_text + str(code))

            token = generate_token(timeout=timedelta(minutes=3), user_identifier=user_identifier)
            return build_response(
                "success",
                "Verification code sent",
                status.HTTP_201_CREATED,
                {'token': token}
            )


class RegistrationType(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RegistrationTypeSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            request.session['registration_data'] = {'account_type': serializer.validated_data.get('account_type')}
            return build_response('success', 'Account type accepted', status.HTTP_202_ACCEPTED)


class RegistrationName(APIView):
    def post(self, request, *args, **kwargs):
        if not request.session.get('registration_data'):
            return build_response('error', 'Resource not found', status.HTTP_404_NOT_FOUND)

        serializer = RegistrationNameSerializer(data=request)
        if serializer.is_valid(raise_exception=True):
            first_name = serializer.validated_data.get("first_name")
            last_name = serializer.validated_data.get("last_name")
            request.session['registration_data']['first_name'] = first_name
            request.session['registration_data']['last_name'] = last_name
            return build_response('success', 'Name accepted', status.HTTP_202_ACCEPTED)


class RegistrationBirthdayGender(APIView):
    def post(self, request, *args, **kwargs):
        if not request.session.get('registration_data'):
            return build_response('error', 'Resource not found', status.HTTP_404_NOT_FOUND)

        serializer = RegistrationBirthdayGenderSerializer(data=request)
        if serializer.is_valid(raise_exception=True):
            gender = serializer.validated_data.get("gender")
            birthday = serializer.validated_data.get("birthday")
            request.session['registration_data']['birthday'] = birthday
            request.session['registration_data']['gender'] = gender
            return build_response('success', 'Birthday and gender accepted', status.HTTP_202_ACCEPTED)


class RegistrationEmail(APIView):
    def get(self, request, *args, **kwargs):
        if not request.session.get('registration_data'):
            return build_response('error', 'Resource not found', status.HTTP_404_NOT_FOUND)

        first_name = request.session['registration_data'].get('first_name')
        last_name = request.session['registration_data'].get('last_name')
        birthday = request.session['registration_data'].get('birthday')

        email_suggestions = generate_unique_email_suggestions(first_name, last_name, birthday)

        return build_response('success', 'Email suggestions', status.HTTP_200_OK,
                              {'email_suggestions': email_suggestions})

    def post(self, request, *args, **kwargs):
        if not request.session.get('registration_data'):
            return build_response('error', 'Resource not found', status.HTTP_404_NOT_FOUND)

        serializer = RegistrationEmailSerializer(data=request)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data.get("email")
            if User.objects.filter(email=email).exists():
                raise build_response('error', 'Email already registered', status.HTTP_409_CONFLICT)

            request.session['registration_data']['email'] = email
            return build_response('success', 'Email accepted', status.HTTP_202_ACCEPTED)


class RegistrationPassword(APIView):
    def post(self, request, *args, **kwargs):
        if not request.session.get('registration_data'):
            return build_response('error', 'Page not found', status.HTTP_404_NOT_FOUND)

        serializer = RegistrationPasswordSerializer(data=request)
        if serializer.is_valid(raise_exception=True):
            password = serializer.validated_data.get("password")
            request.session['registration_data']['password'] = password

            return build_response('success', 'Password accepted', status.HTTP_202_ACCEPTED)


class RegistrationParentEmail(APIView):
    def post(self, request, *args, **kwargs):
        if not request.session.get('registration_data'):
            return build_response('error', 'Page not found', status.HTTP_404_NOT_FOUND)

        serializer = RegistrationParentEmailSerializer(data=request)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data.get("email")
            request.session['registration_data']['parent_email'] = email

            return build_response('success', 'Parent email accepted', status.HTTP_202_ACCEPTED)


class CustomLogin(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')

        user = authenticate(request, email=email, phone_number=phone_number, password=password)

        if user is not None:
            # User authentication successful, proceed with login
            login(request, user)

            # Generate JWT tokens using the custom serializer
            serializer = CustomTokenObtainPairSerializer(
                data={'email': email, 'phone_number': phone_number, 'password': password}
            )
            serializer.is_valid(raise_exception=True)
            tokens = serializer.validated_data

            response_data = {
                'access_token': str(tokens.access_token),
                'refresh_token': str(tokens.refresh_token),
                'user_id': user.id,
                'email': user.email,
                'phone_number': user.phone_number,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class CustomTokenRevokeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail': 'Token successfully revoked.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
