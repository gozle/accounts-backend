import re
import emoji
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


# Function to validate name
def validate_name(value):
    pattern = r'^[\w\s]+$'
    if emoji.emoji_count(value):
        raise ValidationError('Name cannot contain emojis')
    if not re.match(pattern, value):
        raise ValidationError('Name can contain only letters and space')
    if re.search(r'\d', value):
        raise ValidationError("Name can't contain any numbers")


# Function to validate phone number
def validate_phone_number(value):
    pattern = r'^(\+993)\d{8}$'
    if not re.match(pattern, value):
        raise ValidationError('Invalid phone number')


def validate_username(value):
    return RegexValidator(
        regex='^[a-zA-Z0-9_]*$',
        message="Username must be alphanumeric and can only contain underscores",
        code='invalid_username'
    )
