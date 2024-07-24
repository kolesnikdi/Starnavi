from knox.auth import TokenAuthentication
from ninja.security import HttpBearer
from rest_framework.exceptions import AuthenticationFailed


class KnoxAuth(HttpBearer):
    def authenticate(self, request, token):
        knox_auth = TokenAuthentication()
        try:
            user, auth_token = knox_auth.authenticate_credentials(token.encode())
            return user
        except AuthenticationFailed:
            return None
