from rest_framework.views import APIView


class PhoneNumberVerificationAPIView(APIView):
    verification_text = _("Your verification code is: ")

    def get_serializer_class(self, *args, **kwargs):
        return VerificationSerializer(*args, **kwargs)

    def get(self, request):
        phone_number = request.GET.get('phone_number')
        if phone_number is not None:
            random_digit = randint(MIN_VALUE, MAX_VALUE)
            cache.set(
                f"+{phone_number}_verification_code",
                random_digit,
                timeout=60 * 3  # 3 minutes
            )
            text = self.verification_text + str(random_digit)
            sms = SMS(
                text=text,
                dest=phone_number
            )
            response = sms.send()
            return Response(
                {"message": response.get('content')},
                status=response.get("status_code")
            )

        return Response(
            {"message": _("Invalid phone number!")},
            status=status.HTTP_400_BAD_REQUEST
        )

    def post(self, request):
        data = {"is_verified": False}
        serializer = self.get_serializer_class(data=request.data)
        if serializer.is_valid():
            data["is_verified"] = True
            return Response(data, status=status.HTTP_202_ACCEPTED)

        return Response(data, status=status.HTTP_400_BAD_REQUEST)