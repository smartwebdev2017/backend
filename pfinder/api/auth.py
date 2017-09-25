from .models import User


class AlwaysRootBackend(object):
    def authenticate(self, *args, **kwargs):
        """Always returns the `root` user.  DO NOT USE THIS IN PRODUCTION!"""
        print(kwargs.get('username'))
        return User.objects.get(username=kwargs.get('username'))

    def get_user(self, user_id):
        return User.objects.get(username='root')
