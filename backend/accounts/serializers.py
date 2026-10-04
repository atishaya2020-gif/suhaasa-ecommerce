from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from .models import Address, CustomerProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]
        read_only_fields = ["id", "username", "email"]


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150)

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def create(self, validated_data):
        email = validated_data["email"]
        user = User.objects.create_user(
            username=email,
            email=email,
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs["email"].strip().lower()
        user = authenticate(username=email, password=attrs["password"])
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError("This account is inactive.")
        attrs["user"] = user
        return attrs


class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ["phone", "updated_at"]
        read_only_fields = ["updated_at"]


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id", "label", "full_name", "phone", "address_line1", "address_line2",
            "city", "state", "pincode", "is_default", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_pincode(self, value):
        value = value.strip()
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("Enter a valid 6-digit PIN code.")
        return value
