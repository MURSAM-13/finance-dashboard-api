from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from api.models import User


class CustomJWTAuthentication(JWTAuthentication):
    """
    Override the default JWT backend to load our custom User model
    instead of Django's built-in auth.User.
    """

    def get_user(self, validated_token):
        user_id = validated_token.get("user_id")
        if not user_id:
            raise InvalidToken("Token contains no user_id")

        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise InvalidToken("User not found")
