from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.core.exceptions import PermissionDenied

class GoogleSocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        #this method is called when a new user tries to sign up via a social account
        #return false blocks them from creating a new account
        return False