from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .utils import decode_token

class JWTAuthentication(BaseAuthentication):

    def authenticate(self, request):
        header = request.headers.get("Authorization")

        if not header or not header.startswith("Bearer "):
            return None

        token = header.split(" ")[1]

        try:
            payload = decode_token(token)
        except Exception:
            raise AuthenticationFailed("Invalid or expired token")

        request.user = payload
        return (payload, None)
