from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
import os

from demo.models import User, UserProfile, ProfileImage

class Command(BaseCommand):
    help = 'Create sample service provider(s) and profiles with images for testing'

    def handle(self, *args, **options):
        # static images to use
        base = os.path.join(settings.BASE_DIR, 'demo', 'static', 'assets', 'images')
        logo_path = os.path.join(base, 'b1.jpg')
        photo_path = os.path.join(base, 'b2.jpeg')

        u, created = User.objects.get_or_create(
            name='sample_provider',
            defaults={
                'contact': 9999999999,
                'email': 'provider@example.com',
                'city': 'City',
                'create_password': 'x',
                'confirm_password': 'x',
                'user_type': 'service_provider'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created User sample_provider'))
        else:
            self.stdout.write('User sample_provider already exists')

        profile, pcreated = UserProfile.objects.get_or_create(
            user=u,
            defaults={
                'company_name': 'Sample Builders',
                'office_address': '123 Main St',
                'office_number': '9999999999',
                'gst_number': 'GST123',
                'pan_number': 'PAN123',
                'service_type': 'Builders',
                'company_description': 'Sample Builder profile',
            }
        )
        if pcreated:
            self.stdout.write(self.style.SUCCESS(f'Created profile {profile.company_name}'))
        else:
            self.stdout.write('Profile already exists')

        # attach logo if not present
        if profile.logo:
            self.stdout.write('Profile already has a logo')
        else:
            if os.path.exists(logo_path):
                with open(logo_path, 'rb') as f:
                    profile.logo.save(os.path.basename(logo_path), File(f), save=True)
                self.stdout.write(self.style.SUCCESS('Saved logo for profile'))
            else:
                self.stdout.write(self.style.WARNING(f'Logo file not found at {logo_path}'))

        # create a sample ProfileImage
        if os.path.exists(photo_path):
            exists = profile.images.exists()
            if not exists:
                with open(photo_path, 'rb') as f:
                    ProfileImage.objects.create(profile=profile, image=File(f, name=os.path.basename(photo_path)))
                self.stdout.write(self.style.SUCCESS('Created a sample profile image'))
            else:
                self.stdout.write('Profile already has images')
        else:
            self.stdout.write(self.style.WARNING(f'Photo file not found at {photo_path}'))

        self.stdout.write(self.style.SUCCESS('Done'))
