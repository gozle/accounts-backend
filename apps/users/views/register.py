import os
import uuid
from datetime import timedelta, date, datetime

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.core.files import File
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users import User
from apps.users import CustomTokenObtainPairSerializer
from apps.users import (VerificationSerializer, ProfileNameSerializer,
                        AccountTypeSerializer, EmailSerializer,
                        ParentEmailSerializer, PasswordSerializer,
                        ProfileMetadataSerializer,
                        PhoneNumberSerializer)
from apps.users import (generate_token, generate_verification_code,
                        generate_unique_email_suggestions, decode_token, decode_token_with_issuer)
from apps.users import build_response
from apps.users import send_sms, send_email

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

from apps.users import generate_avatar, avatar_to_base64, preprocess_avatar


class Verification(APIView):
    def get_serializer_class(self, *args, **kwargs):
        return VerificationSerializer(*args, **kwargs)

    def post(self, request):
        token_header = request.headers.get(settings.REGISTRATION_TOKEN_HEADER)
        if not token_header:
            return build_response('error', 'token not given', status.HTTP_400_BAD_REQUEST)

        previous_token = decode_token_with_issuer(
            token_header,
            issuers=['registration_phone_number',
                     'registration_parent_email'],
            audience='verification',
        )

        serializer = VerificationSerializer(data=request.data, context={'token_payload': previous_token})
        if serializer.is_valid(raise_exception=True):
            phone_number = serializer.validated_data.get('phone_number').as_e164
            email = serializer.validated_data.get('email')

            payload = previous_token
            payload['verified'] = True
            if phone_number:
                payload['phone_number'] = phone_number
            elif email:
                payload['email'] = email
            payload['exp'] = datetime.utcnow() + timedelta(seconds=settings.REGISTRATION_TOKEN_TIMEOUT)
            payload['iss'] = 'verification'
            del payload['aud']
            token = generate_token(payload)

            response = build_response('ok',
                                      'Verification completed',
                                      status.HTTP_202_ACCEPTED, )
            response[settings.REGISTRATION_TOKEN_HEADER] = token

            return response


class RegistrationAccountType(APIView):
    def post(self, request, *args, **kwargs):
        serializer = AccountTypeSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            payload = {
                'account_type': serializer.validated_data['account_type'],
                'exp': datetime.utcnow() + timedelta(seconds=settings.REGISTRATION_TOKEN_TIMEOUT),
                'iat': datetime.utcnow(),
                'iss': 'registration_account_type',
                'aud': ['registration_phone_number', 'registration_parent_email']
            }
            token = generate_token(payload)

            response = build_response('ok',
                                      'Account type accepted',
                                      status.HTTP_202_ACCEPTED, )
            response[settings.REGISTRATION_TOKEN_HEADER] = token

            return response


class RegistrationParentEmail(APIView):
    email_subject = _('{project_name} registration')
    email_text = _('Your verification code: ')

    def post(self, request, *args, **kwargs):
        token_header = request.headers.get(settings.REGISTRATION_TOKEN_HEADER)
        if not token_header:
            return build_response('error', 'token not given', status.HTTP_400_BAD_REQUEST)

        previous_token = decode_token_with_issuer(
            token_header,
            audience=['registration_parent_email'],
            issuers=['registration_account_type', 'registration_phone_number']
        )
        if not previous_token:
            return build_response('error', 'invalid token', status.HTTP_400_BAD_REQUEST)

        serializer = ParentEmailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data.get("email")

            key = f'registration_code:{email}'
            code = generate_verification_code()
            cache.set(
                key,
                code,
                timeout=settings.REGISTRATION_CODE_TIMEOUT
            )

            send_email.delay(
                email,
                self.email_subject.format(project_name=settings.PROJECT_NAME),
                self.email_text + str(code)
            )

            payload = {
                'exp': datetime.utcnow() + timedelta(seconds=settings.REGISTRATION_CODE_TIMEOUT),
                'email': email,
                'iss': 'registration_parent_email',
                'aud': 'verification'
            }
            token = generate_token(payload)

            response = build_response('ok', 'Verification code sent', status.HTTP_200_OK)
            response[settings.REGISTRATION_TOKEN_HEADER] = token
            return response


class RegistrationPhoneNumber(APIView):
    verification_text = _("{project_name} verification code for registration: ")

    def post(self, request, *args, **kwargs):
        token_header = request.headers.get(settings.REGISTRATION_TOKEN_HEADER)
        if not token_header:
            return build_response('error', 'token not given', status.HTTP_400_BAD_REQUEST)

        previous_token = decode_token_with_issuer(
            token_header,
            audience='registration_phone_number',
            issuers=['registration_account_type', 'registration_parent_email', 'registration_profile_name']
        )
        if not previous_token:
            return build_response('error', 'invalid token', status.HTTP_400_BAD_REQUEST)

        serializer = PhoneNumberSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            phone_number = serializer.validated_data.get("phone_number").as_e164

            key = f'registration_code:{phone_number}'
            code = generate_verification_code()
            cache.set(
                key,
                code,
                timeout=settings.REGISTRATION_CODE_TIMEOUT
            )

            send_sms.delay(
                phone_number,
                self.verification_text.format(project_name=settings.PROJECT_NAME) + str(code)
            )
            payload = previous_token
            payload['exp'] = datetime.utcnow() + timedelta(seconds=settings.REGISTRATION_CODE_TIMEOUT)
            payload['phone_number'] = phone_number
            payload['iss'] = 'registration_phone_number'
            payload['aud'] = 'verification'
            token = generate_token(payload)

            response = build_response('ok', 'Verification code sent', status.HTTP_200_OK)
            response[settings.REGISTRATION_TOKEN_HEADER] = token
            return response


class RegistrationProfileName(APIView):
    def post(self, request, *args, **kwargs):
        token_header = request.headers.get(settings.REGISTRATION_TOKEN_HEADER)
        if not token_header:
            return build_response('error', 'token not given', status.HTTP_400_BAD_REQUEST)

        previous_token = decode_token_with_issuer(
            token_header,
            issuers=['verification', 'registration_profile_metadata']
        )
        if not previous_token:
            return build_response('error', 'invalid token', status.HTTP_400_BAD_REQUEST)

        serializer = ProfileNameSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            first_name = serializer.validated_data.get("first_name")
            last_name = serializer.validated_data.get("last_name")

            payload = previous_token
            payload['first_name'] = first_name
            payload['last_name'] = last_name
            payload['iss'] = 'registration_profile_name'
            payload['aud'] = 'registration_profile_metadata'
            token = generate_token(payload)

            response = build_response('ok',
                                      'First name and last name accepted',
                                      status.HTTP_202_ACCEPTED, )
            response[settings.REGISTRATION_TOKEN_HEADER] = token

            return response


class RegistrationProfileMetadata(APIView):
    def post(self, request, *args, **kwargs):
        token_header = request.headers.get(settings.REGISTRATION_TOKEN_HEADER)
        if not token_header:
            return build_response('error', 'token not given', status.HTTP_400_BAD_REQUEST)

        previous_token = decode_token_with_issuer(
            token_header,
            audience=['registration_profile_metadata'],
            issuers=['registration_profile_name', 'registration_profile_email']
        )
        if not previous_token:
            return build_response('error', 'invalid token', status.HTTP_400_BAD_REQUEST)

        serializer = ProfileMetadataSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            gender = serializer.validated_data.get("gender")
            birthday = serializer.validated_data.get("birthday")

            payload = previous_token
            payload['gender'] = gender
            payload['birthday'] = birthday.strftime("%Y-%m-%d")
            payload['iss'] = 'registration_profile_metadata'
            payload['aud'] = 'registration_email'
            token = generate_token(payload)

            response = build_response('ok',
                                      'Gender and Birthday accepted',
                                      status.HTTP_202_ACCEPTED, )
            response[settings.REGISTRATION_TOKEN_HEADER] = token

            return response


class RegistrationEmail(APIView):
    def get(self, request, *args, **kwargs):
        token_header = request.headers.get(settings.REGISTRATION_TOKEN_HEADER)
        if not token_header:
            return build_response('error', 'token not given', status.HTTP_400_BAD_REQUEST)

        previous_token = decode_token_with_issuer(
            token_header,
            audience=['registration_email'],
            issuers=['registration_profile_metadata', 'registration_password'],
        )
        if not previous_token:
            return build_response('error', 'invalid token', status.HTTP_400_BAD_REQUEST)

        first_name = previous_token.get('first_name')
        last_name = previous_token.get('last_name')
        birthday = date.fromisoformat(previous_token.get('birthday'))

        email_suggestions = generate_unique_email_suggestions(first_name, last_name, birthday)

        return build_response('ok', 'Email suggestions', status.HTTP_200_OK,
                              {'email_suggestions': email_suggestions})

    def post(self, request, *args, **kwargs):
        token_header = request.headers.get(settings.REGISTRATION_TOKEN_HEADER)
        if not token_header:
            return build_response('error', 'token not given', status.HTTP_400_BAD_REQUEST)

        previous_token = decode_token_with_issuer(
            token_header,
            audience=['registration_email'],
            issuers=['registration_profile_metadata', 'registration_password'],
        )
        if not previous_token:
            return build_response('error', 'invalid token', status.HTTP_400_BAD_REQUEST)

        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data.get("email")
            if User.objects.filter(email=email).exists():
                return build_response('error', 'Email already registered', status.HTTP_409_CONFLICT)

            payload = previous_token
            payload['email'] = email
            payload['iss'] = 'registration_email'
            payload['aud'] = 'registration_password'
            token = generate_token(payload)

            response = build_response('ok',
                                      'Email accepted',
                                      status.HTTP_202_ACCEPTED, )
            response[settings.REGISTRATION_TOKEN_HEADER] = token

            return response


# class RegistrationAvatar(APIView):
#     def get(self, request, *args, **kwargs):
#         token_header = request.headers.get(settings.REGISTRATION_TOKEN_HEADER)
#         if not token_header:
#             return build_response('error', 'token not given', status.HTTP_400_BAD_REQUEST)
#
#         previous_token = parse_token(token_header)
#         if not previous_token:
#             return build_response('error', 'invalid token', status.HTTP_400_BAD_REQUEST)
#
#         avatar_tmp_path = generate_avatar(previous_token['first_name'][0])
#         preprocess_avatar(avatar_tmp_path)
#         avatar_base64 = avatar_to_base64(avatar_tmp_path)
#
#         payload = previous_token
#         payload['avatar'] = avatar_tmp_path
#         token = generate_token(payload)
#
#         response = build_response('ok',
#                                   'Generated avatar',
#                                   status.HTTP_200_OK,
#                                   {'avatar': avatar_base64}
#                                   )
#         response[settings.REGISTRATION_TOKEN_HEADER] = token
#
#         return response
#
#     def post(self, request, *args, **kwargs):
#         token_header = request.headers.get(settings.REGISTRATION_TOKEN_HEADER)
#         if not token_header:
#             return build_response('error', 'token not given', status.HTTP_400_BAD_REQUEST)
#
#         previous_token = parse_token(token_header)
#         if not previous_token:
#             return build_response('error', 'invalid token', status.HTTP_400_BAD_REQUEST)
#
#         serializer = AvatarSerializer(data=request.data)
#         if serializer.is_valid():
#             avatar = serializer.validated_data.get("avatar")
#
#             payload = previous_token
#             avatar_tmp_path = avatar.temporary_file_path()
#             payload['avatar'] = avatar_tmp_path
#             preprocess_avatar(avatar_tmp_path)
#             token = generate_token(payload)
#
#             response = build_response('ok',
#                                       'Avatar accepted',
#                                       status.HTTP_202_ACCEPTED)
#             response[settings.REGISTRATION_TOKEN_HEADER] = token
#
#             return response
#
#         response = build_response('ok',
#                                   'Avatar skipped',
#                                   status.HTTP_200_OK)
#         response[settings.REGISTRATION_TOKEN_HEADER] = token_header
#         return response


class RegistrationPassword(APIView):
    def post(self, request, *args, **kwargs):
        token_header = request.headers.get(settings.REGISTRATION_TOKEN_HEADER)
        if not token_header:
            return build_response('error', 'token not given', status.HTTP_400_BAD_REQUEST)

        previous_token = decode_token_with_issuer(
            token_header,
            audience=['registration_password'],
            issuers=['registration_email', 'registration'],
        )
        if not previous_token:
            return build_response('error', 'invalid token', status.HTTP_400_BAD_REQUEST)

        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            password = serializer.validated_data.get("password")

            payload = previous_token
            payload['password'] = password
            payload['iss'] = 'registration_password'
            payload['aud'] = 'registration'
            token = generate_token(payload)

            response = build_response('ok',
                                      'Password accepted',
                                      status.HTTP_202_ACCEPTED, )
            response[settings.REGISTRATION_TOKEN_HEADER] = token

            return response


class Registration(APIView):
    def get(self, request, *args, **kwargs):
        token_header = request.headers.get(settings.REGISTRATION_TOKEN_HEADER)
        if not token_header:
            return build_response('error', 'token not given', status.HTTP_400_BAD_REQUEST)

        previous_token = decode_token_with_issuer(
            token_header,
            audience=['registration'],
            issuers=['registration_password'],
        )
        if not previous_token:
            return build_response('error', 'invalid token', status.HTTP_400_BAD_REQUEST)

        avatar_tmp_path = generate_avatar(previous_token['first_name'][0])
        preprocess_avatar(avatar_tmp_path)
        avatar_base64 = avatar_to_base64(avatar_tmp_path)
        payload = previous_token
        payload['avatar'] = avatar_tmp_path
        token = generate_token(payload)

        response = build_response('ok',
                                  'Confirm account registration',
                                  status.HTTP_200_OK,
                                  {
                                      'data': {
                                          'email': previous_token['email'],
                                          'first_name': previous_token['first_name'],
                                          'last_name': previous_token['last_name'],
                                          'avatar': avatar_base64
                                      }
                                  }
                                  )
        response[settings.REGISTRATION_TOKEN_HEADER] = token
        return response

    def post(self, request, *args, **kwargs):
        token_header = request.headers.get(settings.REGISTRATION_TOKEN_HEADER)
        if not token_header:
            return build_response('error', 'token not given', status.HTTP_400_BAD_REQUEST)

        previous_token = decode_token_with_issuer(
            token_header,
            audience=['registration'],
            issuers=['registration_password'],
        )
        if not previous_token:
            return build_response('error', 'invalid token', status.HTTP_400_BAD_REQUEST)

        user = User(
            account_type=previous_token['account_type'],
            email=previous_token['email'],
            phone_number=previous_token['phone_number'],
            first_name=previous_token['first_name'],
            last_name=previous_token['last_name'],
            birthday=date.fromisoformat(previous_token['birthday']),
            gender=previous_token['gender'],
            parent_email=previous_token.get('parent_email')
        )
        user.set_password(previous_token['password'])

        avatar_tmp_path = previous_token['avatar']
        with open(avatar_tmp_path, 'rb') as avatar_file:
            user.avatar.save((uuid.uuid4().hex + '.png'), File(avatar_file))
        os.remove(avatar_tmp_path)

        user.save()

        return build_response('ok',
                              'Account registered',
                              status.HTTP_201_CREATED, )


class CustomLogin(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')

        user = authenticate(request, email=email, phone_number=phone_number, password=password)

        if user is not None:
            # User authentication okful, proceed with login
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
            return Response({'detail': 'Token okfully revoked.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
