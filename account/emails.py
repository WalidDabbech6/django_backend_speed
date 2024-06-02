from django.conf import settings
from .models import User
from django.core.mail import EmailMessage,get_connection
from django.http import HttpResponse
from rest_framework import status
import logging
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart


# def send_otp_via_email(email):
#     subject = 'Your account verification email'
#     otp = random.randint(1000,9999)
#     message = f'Your otp is {otp}'
#     email_from = settings.EMAIL_HOST_USER_OTP
#     send_mail(subject,message,email_from,[email])
#     user_obj = User.objects.get(email = email)
#     user_obj.otp = otp
#     user_obj.save()

# def send_notification_via_email(orderDetails):
#     subject = 'Payment Notification'
#     message = 'A new payment has been received.'
#     admin_email = 'admin@olataxi.tn'
#     email_from = settings.EMAIL_HOST_USER_NOTIFICATION
#     send_mail(subject, message, email_from,[admin_email])


# def send_confirmation_via_email(orderDetails,client_email):
#     subject = 'Payment Confirmation'
#     message = 'Your payment was successful.'
#     email_from = settings.EMAIL_HOST_USER_PAYMENT
#     send_mail(subject, message, email_from,[client_email])
logger = logging.getLogger(__name__)



def send_email(subject, message, recipient_list,from_email,from_password):
    context = ssl.create_default_context()
    smtp = smtplib.SMTP_SSL(settings.EMAIL_HOST,settings.EMAIL_PORT, context=context)
    smtp.set_debuglevel(1)
    smtp.ehlo()
    smtp.login(user=from_email,password=from_password)

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = recipient_list
    msg['Subject'] = subject
    msg.attach(MIMEText(message))

    to = [recipient_list]
    smtp.sendmail(from_email,
    to,
    msg.as_string())


def send_otp_email(subject, message, recipient_list):
    from_email = settings.EMAIL_HOST_USER_OTP
    from_password = settings.EMAIL_HOST_PASSWORD_OTP
    try:
        send_email(subject, message, recipient_list, from_email, from_password)
        # return HttpResponse(f'OTP email sent successfully {recipient_list}', status=status.HTTP_200_OK)

    except Exception as e:
        return e
        # return HttpResponse("Failed to send OTP email", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
def send_notification_email(subject, message, recipient_list):
    from_email = settings.EMAIL_HOST_USER_NOTIFICATION
    from_password = settings.EMAIL_HOST_PASSWORD_NOTIFICATION
    try:
        send_email(subject, message, recipient_list, from_email, from_password)
    except Exception as e:
        return e

def send_confirmation_email(subject, message, recipient_list):
    from_email = settings.EMAIL_HOST_USER_PAYMENT
    from_password = settings.EMAIL_HOST_PASSWORD_PAYMENT
    try:
        send_email(subject, message, recipient_list, from_email, from_password)
    except Exception as e:
        return e