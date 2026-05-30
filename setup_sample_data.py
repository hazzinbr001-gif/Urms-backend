import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.accounts.models import User
from apps.universities.models import University
from django.contrib.auth.hashers import make_password

def setup():
    # Create sample university
    uni, created = University.objects.get_or_create(
        name="Sample University",
        domain="sample.edu",
        slug="sample-uni",
        is_active=True,
        description="A sample university for testing the URMS platform."
    )
    if created:
        print(f"Created university: {uni.name}")
    else:
        print(f"University {uni.name} already exists.")

    # Create superuser
    username = "admin"
    email = "admin@sample.edu"
    password = "AdminPassword123!"
    
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            university=uni
        )
        print(f"Created superuser: {username} / {password}")
    else:
        print(f"Superuser {username} already exists.")

if __name__ == "__main__":
    setup()
