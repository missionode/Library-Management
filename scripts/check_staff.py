import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings')
django.setup()

from accounts.models import User, MembershipTier

def check_staff():
    for username in ['admin', 'lib_jane']:
        try:
            u = User.objects.get(username=username)
            print(f"User: {u.username}, Role: {u.role}, Tier: {u.membership_tier}")
        except User.DoesNotExist:
            print(f"{username} not found")

if __name__ == '__main__':
    check_staff()
