from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from .models import RefreshToken

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ['id']

    def create(self, validated_data):
        email = validated_data.pop('email')
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        return User.objects.create_user(email=email, username=username, password=password, **validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)

        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        data["user"] = user
        return data

class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.UUIDField()

    def validate_refresh_token(self, value):
        try:
            token = RefreshToken.objects.get(token=value)
        except RefreshToken.DoesNotExist:
            raise serializers.ValidationError("Invalid refresh token.")

        if token.is_expired:
            raise serializers.ValidationError("Refresh token has expired.")

        return value