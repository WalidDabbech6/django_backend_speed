from rest_framework.views import APIView 
from rest_framework.generics import RetrieveUpdateAPIView,CreateAPIView
from rest_framework.response import Response
from .serializers import User,UserSerializer,LoginSerializer,VerifyAccountSerializer
from .emails import send_otp_email
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from django.core import serializers
from rest_framework import status
import json
import random


something_went_wrong = "something went wrong",
class UpdateProfileView(RetrieveUpdateAPIView):

    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, )
    serializer_class = UserSerializer
    def get_object(self):
        return User.objects.get(email=self.request.user)
       




class LoginApi(CreateAPIView):
    serializer_class = LoginSerializer
    permission_classes = []
    def  post (self,request):
        try:
            data = request.data
            serializer = LoginSerializer(data=data)
            if serializer.is_valid():
                email = serializer.data['email']
                password = serializer.data['password']
                user = authenticate(email=email,password=password)
                if user is None:
                    return Response({
                'status':400,
                'message':'Invalid password',
                'data': {}
                },status.HTTP_400_BAD_REQUEST)

                if user.is_verified is False:

                     return Response({
                'status':400,
                'message':'your account is not verified',
                'data': {}
                },status.HTTP_403_FORBIDDEN)

                query_set = User.objects.filter(email=email).values().first()
                user_data = {'id':query_set['id'],
                            'email': query_set['email'],
                            'isVerified':query_set['is_verified'],
                            'otp':query_set['otp'],
                            'first_name': query_set['first_name'],
                            'last_name': query_set['last_name']
                            #  'profile':{
                            #      "ville":query['ville'],
                            #      "gender":query['gender'],
                            #      "job":query['job'],
                            #      'first_name': query['first_name'],
                            #      'last_name': query['last_name'],
                            #      'profile_photo':query['profile_photo']
                            #  }
                        }
                try:
                    refresh = RefreshToken.for_user(user)
                    return Response({
                    'accessToken':f"Bearer {refresh.access_token}",  
                    'user': user_data},status=status.HTTP_200_OK)
                except Exception as e:
                    print(e)
            return Response({
                'status':400,
                'message':something_went_wrong,
                'data': serializer._errors
            },status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)



            
class RegisterApi(CreateAPIView):
    serializer_class = UserSerializer
    def post(self,request):
        try:
            data=request.data
            serializer = UserSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                subject = 'Your account verification email'
                otp = random.randint(1000,9999)
                message = f'Your otp is {otp}'
                user_obj = User.objects.get(email = serializer.data['email'])
                user_obj.otp = otp
                user_obj.save()
                send_otp_email(subject=subject,message=message,recipient_list=serializer.data['email'])
                return Response ({
                    'status':200,
                    'message': 'registration successfully check email',
                    'data':serializer.data,
                },status.HTTP_200_OK)
            
            return Response({
                'status':400,
                'message':something_went_wrong,
                'data': serializer._errors
            },status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)





class VerifyOTP(CreateAPIView): 
    serializer_class = UserSerializer
    def post(self,request):
        try:
            data = request.data
            serializer= VerifyAccountSerializer(data=data)
            if serializer.is_valid():
                email = serializer.data['email']
                otp = serializer.data['otp']
                user  = User.objects.filter(email=email)
                if not user.exists():
                     return Response({
                    'status':400,
                    'message':something_went_wrong,
                    'data': 'invalid email'
                         },status.HTTP_400_BAD_REQUEST)
                if  user[0].otp != otp:
                      return Response({
                    'status':400,
                    'message':'wrong otp',
                    'data': 'wrong otp'
                         },status.HTTP_400_BAD_REQUEST)
                user = user.first()
                user.is_verified = True
                user.save()

                return Response ({
                    'status':200,
                    'message': 'account verified',
                    'data':{},
                },status.HTTP_200_OK)
            
            return Response({
                'status':400,
                'message':something_went_wrong,
                'data': serializer._errors
            },status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
