from django.core.management.base import BaseCommand
from posts.models import Community

class Command(BaseCommand):
    help = 'Update member count for all communities'

    def handle(self, *args, **kwargs):
        for community in Community.objects.all():
            community.update_member_count()
            self.stdout.write(self.style.SUCCESS(f'Updated {community.name}: {community.member_count} members'))
