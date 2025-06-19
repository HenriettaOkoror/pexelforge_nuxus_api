from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

def logout_all_sessions(user):
    for token in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=token)