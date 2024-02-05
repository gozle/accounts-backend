def get_valid_phone_number(number):
    if len(number) == 11:
        return '+' + number
    elif len(number) == 8:
        return '+993' + number
    elif len(number) == 9:
        return '+993' + number[1:]
    return number
