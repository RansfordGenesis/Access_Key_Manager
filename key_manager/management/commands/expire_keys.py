from django.core.management.base import BaseCommand
from key_manager.models import AccessKey
from django.utils import timezone

class Command(BaseCommand):
    help = 'Expire active keys whose expiry date is due'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        expired_keys = AccessKey.objects.filter(expiry_date__lt=now, status='active')

        for key in expired_keys:
            key.status = 'expired'
            key.save()
            self.stdout.write(self.style.SUCCESS(f'Key {key.key} expired'))

        if not expired_keys.exists():
            self.stdout.write(self.style.SUCCESS('No keys to expire'))
