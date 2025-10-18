from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User

class GoogleSocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        #this method is called when a new user tries to sign up via a social account
        #return false blocks them from creating a new account

        email = sociallogin.account.extra_data.get('email')
        
        #if they exist, allow it. 
        return User.objects.filter(email=email).exists()


    def get_connect_redirect_url(self, request, socialaccount):
        #returns the URL to redirect to after successful social account connect.
        return reverse('tasks:matrix')