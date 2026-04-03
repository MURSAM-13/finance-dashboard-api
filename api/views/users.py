from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.models import User
from api.serializers import UserSerializer, CreateUserSerializer, UpdateUserSerializer
from api.permissions import IsAdmin


class UserListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        users = User.objects.all()
        return Response(UserSerializer(users, many=True).data)

    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class UserDetailView(APIView):
    permission_classes = [IsAdmin]

    def _get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def get(self, request, user_id):
        user = self._get_user(user_id)
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(UserSerializer(user).data)

    def put(self, request, user_id):
        user = self._get_user(user_id)
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Prevent self-demotion
        if user.id == request.user.id and request.data.get("role") not in (None, User.ADMIN):
            return Response({"error": "You can't demote yourself"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UpdateUserSerializer(instance=user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        user = serializer.save()
        return Response(UserSerializer(user).data)

    def delete(self, request, user_id):
        user = self._get_user(user_id)
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if user.id == request.user.id:
            return Response({"error": "You can't delete your own account"}, status=status.HTTP_400_BAD_REQUEST)

        user.delete()
        return Response({"message": "User deleted"})


class UserStatusView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if user.id == request.user.id:
            return Response({"error": "You can't change your own active status"}, status=status.HTTP_400_BAD_REQUEST)

        is_active = request.data.get("is_active")
        if not isinstance(is_active, bool):
            return Response({"error": "is_active must be true or false"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        user.is_active = is_active
        user.save()

        label = "activated" if is_active else "deactivated"
        return Response({"message": f"User {label}", "user": UserSerializer(user).data})
