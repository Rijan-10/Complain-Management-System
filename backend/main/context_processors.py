from main.models import Profile


def user_info(request):
    user = request.user
    is_admin = False
    if user.is_authenticated:
        try:
            full_name = user.profile.full_name or user.first_name or user.username
            is_admin = user.profile.role == 'admin'
        except Profile.DoesNotExist:
            full_name = user.first_name or user.username
        return {'full_name': full_name, 'is_admin': is_admin}
    return {'full_name': '', 'is_admin': is_admin}
