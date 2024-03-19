from ipware import get_client_ip

from django.conf import settings
from django.core.cache import cache
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from phonenumber_field import serializerfields

from apps.users import MAX_VALUE, MIN_VALUE
from apps.users import validate_name


class VerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    phone_number = serializerfields.PhoneNumberField(required=False)
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

        # user_agent = self.context.get('request').user_agent.ua_string
        # ip_address, is_routable = get_client_ip(self.context.get('request'))

        token_payload = self.context.get('token_payload')
        # token_user_agent = payload.get('user_agent')
        # token_ip_address = payload.get('ip_address')

        # if (token_user_agent != user_agent) or (token_ip_address != ip_address):
        #     raise serializers.ValidationError({'token': _('Token is invalid or expired')})

        if token_payload.get('email') != email:
            raise serializers.ValidationError({'email': _('Invalid email')})
        elif token_payload.get('phone_number') != phone_number:
            raise serializers.ValidationError({'phone_number': _('Invalid phone number')})

        key = f'registration_code:{phone_number or email}'
        verification_code = cache.get(key)

        if not verification_code:
            raise serializers.ValidationError({'code': _('Verification code is invalid or expired')})

        if int(verification_code) != int(code):
            raise serializers.ValidationError({'code': _('Verification code is invalid or expired')})
        else:
            cache.delete(key)

        return super().validate(attrs)


class AccountTypeSerializer(serializers.Serializer):
    TYPES = [
        ('personal', 'Personal Account'),
        ('child', 'For child')
    ]
    account_type = serializers.ChoiceField(choices=TYPES, default='personal')


class PhoneNumberSerializer(serializers.Serializer):
    phone_number = serializerfields.PhoneNumberField()


class ProfileNameSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=40, validators=[validate_name])
    last_name = serializers.CharField(max_length=40, validators=[validate_name], required=False)


class ProfileMetadataSerializer(serializers.Serializer):
    GENDERS = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('N', 'Not specified')
    ]
    birthday = serializers.DateField()
    gender = serializers.ChoiceField(choices=GENDERS, default='N')


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ParentEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class AvatarSerializer(serializers.Serializer):
    avatar = serializers.ImageField()


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=8, max_length=50)
    password_confirmation = serializers.CharField(min_length=8, max_length=50)

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirmation = attrs.get('password_confirmation')

        if password != password_confirmation:
            raise serializers.ValidationError({'password': _('Passwords don\'t match')})

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
