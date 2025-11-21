from django.contrib.auth.backends import BaseBackend
from .models import UserCustom

class UserCustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserCustom.objects.get(username=username, password=password)
            return user
        except UserCustom.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return UserCustom.objects.get(pk=user_id)
        except UserCustom.DoesNotExist:
            return None
