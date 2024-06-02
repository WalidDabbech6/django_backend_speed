from django.shortcuts import render
from rest_framework import generics , status, views
from account.emails import send_confirmation_email,send_notification_email

import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from account.models import User
from forms.models import Booking

# Create your views here.
class MakePaymentApiView(views.APIView):
    permission_classes = (IsAuthenticated,)
    def post(self,request):
        host = request.get_host()
        print("host")
        print(host)
        WEB_URL = settings.WEB_URL_COM
        if host == settings.DOMAIN_NAME_COM or host == settings.WWW_DOMAINE_NAME_COM:
            WEB_URL= settings.WEB_URL_COM
        elif  host == settings.DOMAIN_NAME_TN or host == settings.WWW_DOMAINE_NAME_TN:
            WEB_URL= settings.WEB_URL_TN
        user = User.objects.get(email=self.request.user)
        try:
            bookig = Booking.objects.get(pk=request.data["order_id"])
        except Booking.DoesNotExist:
            return Response({"error": "Order does not exist"}, status=status.HTTP_404_NOT_FOUND)
        if bookig.payed == True:
            return Response({"error": "Order already payed"}, status=status.HTTP_400_BAD_REQUEST)
        headers = {
             'x-api-key':f'{settings.API_KEY}',
        }
        data = {
            "receiverWalletId": f'{settings.WALLET_ID}',
            "token": "TND",
            "amount": bookig.price * 1000,
            "type": "immediate",
            "description": "payment description",
            "acceptedPaymentMethods": [
                "wallet",
                "bank_card",
                "e-DINAR"
            ],
            "lifespan": 10,
            "checkoutForm": 'false',
            "addPaymentFeesToAmount": 'true',
            "firstName": f'{user.first_name}',
            "lastName": f'{user.last_name}',
            "phoneNumber": f'{user.phone}',
            "email": f'{user.email}',
            "orderId": f'{bookig.pk}',
            "webhook": "https://merchant.tech/api/notification_payment",
            "silentWebhook": 'true',
            "successUrl": f'{WEB_URL}/success',
            "failUrl": f'{WEB_URL}/fail',
            "theme": "light"
        }
        response = requests.post(f'{settings.PAYMENT_URL}/payments/init-payment', data=data,headers=headers)
        data = response.json()
        if response.status_code == 200:
            bookig.payment_ref = data["paymentRef"]
            bookig.save()
            return Response(data,status.HTTP_200_OK)

        else:
            return Response(data,status.HTTP_400_BAD_REQUEST)
        

class VerifyPaymentApiView(views.APIView):
    permission_classes = (IsAuthenticated,)
    def get(self,request,pk):
        host = request.get_host()
        WEB_URL = settings.WEB_URL_COM
        if host == settings.DOMAIN_NAME_COM or host == settings.WWW_DOMAINE_NAME_COM:
            WEB_URL= settings.WEB_URL_COM
        elif  host == settings.DOMAIN_NAME_TN or host == settings.WWW_DOMAINE_NAME_TN:
            WEB_URL= settings.WEB_URL_TN
        response = requests.get(f'{settings.PAYMENT_URL}/payments/{pk}')
        data = response.json()
        if response.status_code == 200:
            if (data['payment']['status'] == 'completed' and data['payment']['transactions'][0]['status'] == 'success'):
                try:
                    bookig = Booking.objects.get(pk=data['payment']['orderId'])
                except Booking.DoesNotExist:
                    return Response({"error": "Order does not exist"}, status=status.HTTP_404_NOT_FOUND)
                if (bookig.payed == False):
                    # send_cofirmation_via_email(bookig);
                    notification_details = f"Booking ID: {bookig.id}\nPrix: {bookig.price}\nDate: {bookig.date}\nTime: {bookig.booking_time}\nClient:\n prénom:{bookig.user.first_name}\nnom:{bookig.user.last_name}\ntel:{bookig.user.phone}\nemail:{bookig.user.email}"
                    send_notification_email("New Payment Notification",notification_details,settings.EMAIL_HOST_USER_ADMIN)
                    payment_details = f"Booking ID: {bookig.id}\nPrix: {bookig.price}\nDate: {bookig.date}\nTime: {bookig.booking_time}\nUrl:{WEB_URL}/payment/{data['payment']['orderId']}"
                    send_confirmation_email("Payment Confirmation",payment_details,bookig.user.email)
                bookig.payed = True
                bookig.save()
                return Response(data,status.HTTP_200_OK)
            return Response(data,status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data,status.HTTP_400_BAD_REQUEST)
