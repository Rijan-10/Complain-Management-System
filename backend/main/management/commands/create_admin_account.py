import secrets
import string

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from main.models import Profile

User = get_user_model()

DEFAULT_EMAIL = 'admin@gmail.com'


def generate_phone():
    return '98' + ''.join(secrets.choice(string.digits) for _ in range(8))


class Command(BaseCommand):
    help = 'Create (or reset) an admin account on the live database.'

    def add_arguments(self, parser):
        parser.add_argument('--email', default=DEFAULT_EMAIL)
        parser.add_argument('--password', required=True,
                            help='Admin password (provided at runtime, never stored).')
        parser.add_argument('--phone', default=None,
                            help='Random 10-digit number is generated when omitted.')
        parser.add_argument('--full-name', default='Admin CMS')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        full_name = options['full_name']
        phone = options['phone'] or generate_phone()

        user, created = User.objects.get_or_create(
            email__iexact=email,
            defaults={
                'username': email,
                'email': email,
                'first_name': full_name,
            },
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(
                f'Created user {email} (id={user.id}).'))
        else:
            user.first_name = full_name
            user.email = email
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(
                f'Updated existing user {email} (id={user.id}); '
                f'password reset to "{password}".'))

        profile, _ = Profile.objects.get_or_create(user=user, defaults={
            'role': 'admin',
            'full_name': full_name,
            'phone': phone,
            'account_status': 'active',
        })
        profile.role = 'admin'
        profile.full_name = full_name
        profile.phone = phone
        profile.account_status = 'active'
        profile.save()

        self.stdout.write(self.style.SUCCESS(
            f'Admin account ready:\n'
            f'  email    : {email}\n'
            f'  password : ******** (set at runtime)\n'
            f'  phone    : {phone}\n'
            f'  role     : admin\n'
            f'  status   : active'))
