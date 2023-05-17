from django.shortcuts import render
from rest_framework.views import APIView 
from rest_framework.generics import UpdateAPIView, ListAPIView,RetrieveUpdateAPIView
from rest_framework.response import Response
from .serializers import *
from .emails import *
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from django.core import serializers


class UpdateProfileView(RetrieveUpdateAPIView):

    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, )
    serializer_class = UserProfileSerializer
    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)
       




class LoginApi(APIView):
    serializer_class = LoginSerializer
    def post(self,request):
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
                })
                if user.is_verified is False:
                     return Response({
                'status':400,
                'message':'your account is not verified',
                'data': {}
                })
                refresh = RefreshToken.for_user(user)
                query_set = User.objects.filter(email=email).values().first()
                query = UserProfile.objects.filter(user=user).values().first()
                print(query)
                userData = {'id':query_set['id'],
                            'email': query_set['email'],
                            'password':query_set['password'],
                            'isVerified':query_set['is_verified'],
                             'otp':query_set['otp'],
                             'profile':{
                                 "ville":query['ville'],
                                 "gender":query['gender'],
                                 "job":query['job'],
                                 'first_name': query['first_name'],
                                 'last_name': query['last_name'],
                                 'profile_photo':query['profile_photo']
                             }
                            }
                return Response({
                'accessToken':str(refresh.access_token),  
                'user': userData,
                })
            
            return Response({
                'status':400,
                'message':'something went wrong',
                'data': serializer._errors
            })
        except Exception as e:
            print(e)



            
class RegisterApi(APIView):
    serializer_class = UserSerializer
    def post(self,request):
        try:
            data=request.data
            serializer = UserSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                send_otp_via_email(serializer.data['email'])
                return Response ({
                    'status':200,
                    'message': 'registration successfully check email',
                    'data':serializer.data,
                })
            
            return Response({
                'status':400,
                'message':'something went wrong',
                'data': serializer._errors
            })
        except Exception as e:
            print(e)





class VerifyOTP(APIView): 
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
                    'message':'something went wrong',
                    'data': 'invalid email'
                         })
                if not user[0].otp == otp:
                      return Response({
                    'status':400,
                    'message':'something went wrong',
                    'data': 'wrong otp'
                         })
                user = user.first()
                user.is_verified = True
                user.save()

                return Response ({
                    'status':200,
                    'message': 'account verified',
                    'data':{},
                })
            
            return Response({
                'status':400,
                'message':'something went wrong',
                'data': serializer._errors
            })
        except Exception as e:
            print(e)
