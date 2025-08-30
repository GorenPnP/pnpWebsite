from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

class EmailBackend(ModelBackend):
    """ allows to use the user's email as username during login """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        print(username)
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None