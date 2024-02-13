from rest_framework.response import Response


def get_valid_phone_number(number):
    if len(number) == 11:
        return '+' + number
    elif len(number) == 8:
        return '+993' + number
    elif len(number) == 9:
        return '+993' + number[1:]
    return number


def build_response(status, message, http_status, additional_data=None):
    if additional_data is None:
        additional_data = {}
    data = {'status': status, 'message': message, **additional_data}
    return Response(status=http_status, data=data)
