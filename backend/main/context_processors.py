from main.models import Profile


def user_info(request):
    user = request.user
    if user.is_authenticated:
        try:
            full_name = user.profile.full_name or user.first_name or user.username
        except Profile.DoesNotExist:
            full_name = user.first_name or user.username
        return {'full_name': full_name}
    return {'full_name': ''}
