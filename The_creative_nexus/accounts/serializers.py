from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(
        source='get_role_display', read_only=True)

    class Meta:
        model = UserProfile
        fields = (
            'id', 'user', 'role', 'role_display', 'bio', 'profile_picture',
            'location', 'phone', 'website', 'skills', 'years_experience',
            'portfolio_url', 'is_verified', 'verification_date', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at',
                            'updated_at', 'verification_date')


class CustomUserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'profile', 'email_verified', 'created_at')
        read_only_fields = ('id', 'email_verified', 'created_at')


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    role = serializers.CharField(write_only=True, required=False, default='creator')

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name',
                  'password', 'password_confirm', 'role')

    def validate(self, data):
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError(
                {'password': 'Passwords do not match'})
        return data

    def create(self, validated_data):
        role = validated_data.pop('role', 'creator')
        user = CustomUser.objects.create_user(**validated_data)
        # Update the auto-created profile with the specified role
        if hasattr(user, 'profile'):
            user.profile.role = role
            user.profile.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data['email']
        password = data['password']
        
        # Try to get user by email
        try:
            user = CustomUser.objects.get(email=email)
            # Now authenticate with username and password
            user = authenticate(username=user.username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid password')
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError('No user found with this email')
        
        data['user'] = user
        return data


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            'bio', 'profile_picture', 'location', 'phone', 'website',
            'skills', 'years_experience', 'portfolio_url'
        )
