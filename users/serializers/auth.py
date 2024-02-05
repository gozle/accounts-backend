from django.core.cache import cache
from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True)
    username = serializers.CharField(max_length=30, required=True)
    phone_number = None  # TODO
    balance = serializers.FloatField(default=0)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class VerificationSerializer(serializers.Serializer):
    phone_number = serializerfields.PhoneNumberField()
    code = serializers.IntegerField(
        validators=[
            MinValueValidator(MIN_VALUE),
            MaxValueValidator(MAX_VALUE)
        ]
    )

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        code = attrs.get('code')
        verification_code = cache.get(f'{phone_number}_verification_code')
        if verification_code != code:
            raise serializers.ValidationError(
                {"code": _("Verification code didn't match.")},
            )

        return super().validate(attrs)
