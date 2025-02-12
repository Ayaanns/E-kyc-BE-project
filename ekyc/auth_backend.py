from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class EmailBackend(ModelBackend):
    # This class is used in Django AUTHENTICATION_BACKENDS
    def authenticate(self, request, email=None, password=None, **kwargs):
        """
        Authenticate a user based on email and password.

        Args:
            request: HttpRequest object.
            email (str): User's email address.
            password (str): User's password.
            **kwargs: Additional keyword arguments.

        Returns:
            User object if authentication is successful, otherwise None.
        """
        try:
            # Try to get the user with the given email
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Return None if the user does not exist
            return None

        # Check if the provided password is correct
        if user.check_password(password):
            return user

    def get_user(self, user_id):
        """
        Retrieve a user by their ID.

        Args:
            user_id (int): User's ID.

        Returns:
            User object if found, otherwise None.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
