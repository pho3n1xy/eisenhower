from allauth.socialaccount.models import SocialAccount

def google_connection_processor(request):
    '''
    Checks if the logged-in user has a google account connected.
    '''
    is_google_connected = False
    if request.user.is_authenticated:
        is_google_connected = SocialAccount.objects.filter(
            user=request.user,
            provider='google'
        ).exists()

    return {'is_google_connected': is_google_connected}