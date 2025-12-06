from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()

class EmailOrUsernameBackend(ModelBackend):
    """ allows to use the user's email as username during login """
    
    def authenticate(self, request, username=None, password=None, **kwargs):

        # try getting value from kwargs, e.g. by key 'email'
        if username is None: username = kwargs.get(User.USERNAME_FIELD)

        # not enough information to work with
        if username is None or password is None: return

        try:
            user = User._default_manager.get(email=username)
        except User.DoesNotExist:
            try:
                user = User._default_manager.get(username=username)
            except User.DoesNotExist:
                # Run the default password hasher once to reduce the timing
                # difference between an existing and a nonexistent user (#20760).
                User().set_password(password)
                return None
    
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
