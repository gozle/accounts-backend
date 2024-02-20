from ipware import get_client_ip
from django.conf import settings
from django.core.cache import cache
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from phonenumber_field import serializerfields

from users.models import User
from users.utils.auth import parse_token
from users.utils.sms import MAX_VALUE, MIN_VALUE
from users.validators.auth import validate_name


class VerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    phone_number = serializerfields.PhoneNumberField(required=False)
    user_agent = serializers.CharField(required=False)
    code = serializers.IntegerField(
        validators=[
            MinValueValidator(MIN_VALUE),
            MaxValueValidator(MAX_VALUE)
        ],
        required=False
    )

    def validate(self, attrs):
        code = attrs.get('code')
        email = attrs.get('email')
        phone_number = attrs.get('phone_number')
        token = self.context.get('request').data.get('token')
        # user_agent = self.context.get('request').user_agent.ua_string
        # ip_address, is_routable = get_client_ip(self.context.get('request'))

        if token:
            payload = parse_token(token)
            if not payload:
                raise serializers.ValidationError({'token': _('Token is invalid or expired')})
            user_identifier = payload.get('user_identifier')
            # token_user_agent = payload.get('user_agent')
            # token_ip_address = payload.get('ip_address')
            #
            # if (token_user_agent != user_agent) or (token_ip_address != ip_address):
            #     raise serializers.ValidationError({'token': _('Token is invalid or expired')})

            key = f'verification_code:{user_identifier}'
            value = cache.get(key)

            if not value:
                raise serializers.ValidationError({'code': _('Verification code is invalid or expired')})

            verification_code, attempt = value.split(':')

            if int(verification_code) != int(code):
                raise serializers.ValidationError({'code': _('Invalid verification code')})
            else:
                cache.delete(f'verification_code:{user_identifier}')

            return super().validate(attrs)

        if email and not phone_number:
            raise serializers.ValidationError({'email': _('Email is required')})
        elif phone_number and not email:
            raise serializers.ValidationError({'phone_number': _('Phone number is required')})
        elif not email and not phone_number:
            raise serializers.ValidationError({'phone_number': _('Phone number is required'),
                                               'email': _('Email is required')})

        return super().validate(attrs)


class RegistrationTypeSerializer(serializers.Serializer):
    TYPES = [
        ('personal', 'Personal Account'),
        ('child', 'For child')
    ]
    account_type = serializers.ChoiceField(choices=TYPES, default='personal')


class RegistrationNameSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=40, validators=[validate_name])
    last_name = serializers.CharField(max_length=40, validators=[validate_name], required=False)


class RegistrationBirthdayGenderSerializer(serializers.Serializer):
    GENDERS = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('N', 'Not specified')
    ]
    birthday = serializers.DateField()
    gender = serializers.ChoiceField(choices=GENDERS, default='N')


class RegistrationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get('email')

        if not email:
            raise serializers.ValidationError({'email': _('Email is required')})

        return super().validate(attrs)


class RegistrationPasswordSerializer(serializers.Serializer):
    password = serializers.CharField()
    password_confirmation = serializers.CharField()

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirmation = attrs.get('password_confirmation')

        if password != password_confirmation:
            raise serializers.ValidationError({'password': _('Passwords don\'t match')})

        return super().validate(attrs)


class RegistrationParentEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get('email')

        if not email:
            raise serializers.ValidationError({'email': _('Email is required')})

        return super().validate(attrs)


class UserSerializer(serializers.Serializer):
    GENDERS = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('N', 'Not specified')
    ]
    THEMES = [
        ('dark', 'Dark'),
        ('light', 'Light')
    ]
    LANGUAGES = [
        ('en', 'English'),
        ('ru', 'Russian'),
        ('tk', 'Turkmen')
    ]

    id = serializers.UUIDField(read_only=True)
    email = serializers.EmailField()
    phone_number = serializerfields.PhoneNumberField(required=False)
    password = serializers.CharField(write_only=True)
    password_confirmation = serializers.CharField(write_only=True)

    # SECURITY
    two_factor_auth = serializers.BooleanField(default=False)
    recovery_email = serializers.EmailField(required=False)

    # PROFILE INFO
    first_name = serializers.CharField()
    last_name = serializers.CharField(required=False)
    avatar = serializers.ImageField(required=False)
    birthday = serializers.DateField()
    gender = serializers.ChoiceField(choices=GENDERS, default='N')

    # USER SETTINGS
    theme = serializers.ChoiceField(choices=THEMES, default='light')
    language = serializers.ChoiceField(choices=LANGUAGES, default='tk')
