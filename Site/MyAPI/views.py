from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import RefreshToken
from .serializers import UserSerializer, LoginSerializer, RefreshTokenSerializer
from .authentication import create_access_token
from constance import config

from rest_framework.permissions import AllowAny


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'id': user.id, 'email': user.email}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(email=serializer.validated_data['email'], password=serializer.validated_data['password'])
            if not user:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

            access_token = create_access_token(user)
            refresh_token = RefreshToken.objects.create(user=user, expires_at=timezone.now() + timezone.timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS))

            return Response({
                'access_token': access_token,
                'refresh_token': str(refresh_token.token)
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        if serializer.is_valid():
            refresh_token = RefreshToken.objects.filter(token=serializer.validated_data['refresh_token']).first()

            if not refresh_token or refresh_token.is_expired:
                return Response({'error': 'Invalid or expired Refresh Token'}, status=status.HTTP_401_UNAUTHORIZED)

            user = refresh_token.user

            RefreshToken.objects.filter(user=user).delete()

            access_token = create_access_token(user)
            new_refresh_token = RefreshToken.objects.create(user=user, expires_at=timezone.now() + timezone.timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS))

            return Response({
                'access_token': access_token,
                'refresh_token': str(new_refresh_token.token)
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        if serializer.is_valid():
            RefreshToken.objects.filter(token=serializer.validated_data['refresh_token']).delete()
            return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)