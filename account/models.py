from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import UserManager
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail 
from django.db.models.signals import post_save
from django.conf import settings

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):

    email_plaintext_message = "{}?token={}".format(reverse('password_reset:reset-password-request'), reset_password_token.key)

    send_mail(
        # title:
        "Password Reset for {title}".format(title="Application"),
        # message:
        email_plaintext_message,
        # from:
        "noreply@somehost.local",
        # to:
        [reset_password_token.user.email]
    )

class User(AbstractUser):
    username = None
    email = models.EmailField( unique=True)
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6 , null=True, blank=True)
    
    

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    def name(self):
        return self.first_name + ' ' + self.last_name

    def __str__(self):
        return self.email
    

def upload_location(instance, filename):
    filebase, extension = filename.split('.')
    return 'users/%s/profile_photo.%s' % (instance.user.id, extension)


# class UserProfile(models.Model):
#       user =  models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
#       ville = models.CharField(blank=True, max_length=250)
#       gender = models.BooleanField(default=True)
#       job = models.CharField(blank=True, max_length=250)
#       first_name= models.CharField(blank=True, max_length=250)
#       last_name= models.CharField(blank=True, max_length=250)
#       profile_photo = models.FileField(
#       upload_to=upload_location, null=True, blank=True
#     )  
    


# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         UserProfile.objects.create(
#             user = instance
#         )