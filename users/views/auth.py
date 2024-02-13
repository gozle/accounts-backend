from random import randint

from django.contrib.auth import authenticate, login
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers.jwt import CustomTokenObtainPairSerializer
from users.serializers.auth import VerificationSerializer
from users.utils.sms import MIN_VALUE, MAX_VALUE
from users.utils.auth import generate_verification_token
from users.utils.functions import build_response
from users.tasks import send_sms, send_email

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated


class Verification(APIView):
    verification_text = _("Your verification code is: ")

    def get_serializer_class(self, *args, **kwargs):
        return VerificationSerializer(*args, **kwargs)

    def post(self, request):
        serializer = VerificationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            token = serializer.validated_data.get("token")
            method = serializer.validated_data.get("method")
            email = serializer.validated_data.get("email")
            phone_number = serializer.validated_data.get("phone_number")

            if token:
                next_token = ""
                # TODO: After verification, create and return another token to continue registration
                return build_response(
                    "verified",
                    "Verification is complete",
                    status.HTTP_202_ACCEPTED,
                    {'token': next_token}
                )

            if method == 'email':
                key = f"verification_code:{email}"
            else:
                key = f"verification_code:{phone_number.as_e164}"

            code = randint(MIN_VALUE, MAX_VALUE)
            cache.set(
                key,
                code,
                timeout=60 * 3  # 3 minutes
            )
            send_sms.delay(phone_number.as_e164, self.verification_text + str(code))
            token = generate_verification_token(method, email if method == 'email' else phone_number.as_e164)
            return build_response(
                "pending",
                "Verification code sent",
                status.HTTP_201_CREATED,
                {'token': token}
            )


class Register(APIView):
    def post(self, request, *args, **kwargs):
        method = request.data.get('method')
        token = request.data.get('token')
        code = request.data.get('code')

        if method not in ['email', 'phone_number']:
            message = {'status': 'error', 'message': 'Invalid verification method!'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        if not token:
            pass


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
