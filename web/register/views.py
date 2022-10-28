import datetime
import jwt
from .models import User
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer


class RegisterView(APIView):
    def post(self, request):
        serializer = serializers.ModelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response


class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).split()

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=300),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256').decode('utf-8')

        response = Response()

        response.set_cookie(key=jwt, volume=token, httponly=True)
        response.data = {
            'jwt': token
        }

        return Response


class UserView(APIView):
    def get(self, request, payload):
        token = request.COOKIES.get('jwt')

        user = User.objects.filter(id=payload['id']).first()

        serializer = UserSerializer(user)
        return Response(serializer.data)


class Logout(APIView):
    def post(self, request):
        response = Response
        response.delete_cookie('jwt')
        response.data = {
            'message': 'успешно'
        }

