from django.core.cache import cache
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from phonenumber_field import serializerfields

from users.utils.auth import parse_verification_token
from users.utils.sms import MAX_VALUE, MIN_VALUE


class VerificationSerializer(serializers.Serializer):
    method = serializers.ChoiceField(choices=[('email', 'Email'), ('phone_number', 'Phone number')], required=False)
    email = serializers.EmailField(required=False)
    phone_number = serializerfields.PhoneNumberField(required=False)
    token = serializers.CharField(required=False)
    code = serializers.IntegerField(
        validators=[
            MinValueValidator(MIN_VALUE),
            MaxValueValidator(MAX_VALUE)
        ],
        required=False
    )

    def validate(self, attrs):
        method = attrs.get('method')
        token = attrs.get('token')
        code = attrs.get('code')
        email = attrs.get('email')
        phone_number = attrs.get('phone_number')

        if token:
            payload = parse_verification_token(token)
            if not payload:
                raise serializers.ValidationError({'token': _('Token is invalid or expired')})
            method = payload.get('method')
            user_identifier = payload.get('user_identifier')

            verification_code = cache.get(f'verification_code:{user_identifier}')
            if not verification_code:
                raise serializers.ValidationError({'code': _('Verification code is invalid or expired')})
            if int(verification_code) != int(code):
                raise serializers.ValidationError({'code': _('Invalid verification code')})

            return super().validate(attrs)

        if method not in ['email', 'phone_number']:
            raise serializers.ValidationError({'method': _('Invalid verification method')})

        if method == 'email' and not email:
            raise serializers.ValidationError({'email': _('Email is required')})

        if method == 'phone_number' and not phone_number:
            raise serializers.ValidationError({'phone_number': _('Phone number is required')})

        return super().validate(attrs)
