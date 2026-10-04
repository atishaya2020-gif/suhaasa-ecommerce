from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from commerce.views import merge_guest_into_user, session_payload

from .models import Address, CustomerProfile
from .serializers import AddressSerializer, CustomerProfileSerializer, LoginSerializer, RegisterSerializer, UserSerializer

User = get_user_model()


def auth_payload(user, request):
    refresh = RefreshToken.for_user(user)
    guest_token = request.META.get("HTTP_X_SUHAASA_GUEST_TOKEN", "").strip()
    session = merge_guest_into_user(user, guest_token or None)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": UserSerializer(user).data,
        "commerce": session_payload(session),
    }


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(auth_payload(user, request), status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(auth_payload(serializer.validated_data["user"], request))


class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        session = merge_guest_into_user(request.user, None)
        profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
        return Response({
            "user": UserSerializer(request.user).data,
            "profile": CustomerProfileSerializer(profile).data,
            "commerce": session_payload(session),
        })

    def patch(self, request):
        user = request.user
        user_serializer = UserSerializer(user, data=request.data, partial=True)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()
        profile, _ = CustomerProfile.objects.get_or_create(user=user)
        profile_serializer = CustomerProfileSerializer(profile, data=request.data, partial=True)
        profile_serializer.is_valid(raise_exception=True)
        profile_serializer.save()
        return Response({"user": user_serializer.data, "profile": profile_serializer.data})


class AddressListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(AddressSerializer(request.user.addresses.all(), many=True).data)

    def post(self, request):
        serializer = AddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        address = serializer.save(user=request.user)
        return Response(AddressSerializer(address).data, status=status.HTTP_201_CREATED)


class AddressDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):
        return Address.objects.filter(user=request.user, pk=pk).first()

    def patch(self, request, pk):
        address = self.get_object(request, pk)
        if not address:
            return Response({"detail": "Address not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = AddressSerializer(address, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        return Response(AddressSerializer(serializer.save()).data)

    def delete(self, request, pk):
        address = self.get_object(request, pk)
        if not address:
            return Response({"detail": "Address not found."}, status=status.HTTP_404_NOT_FOUND)
        was_default = address.is_default
        address.delete()
        if was_default:
            replacement = request.user.addresses.order_by("-updated_at").first()
            if replacement:
                replacement.is_default = True
                replacement.save(update_fields=["is_default", "updated_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)
