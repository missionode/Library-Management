import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings')
django.setup()

from accounts.models import User

def reset_members():
    members = User.objects.filter(role='MEMBER')
    count = members.count()
    members.delete()
    print(f"Deleted {count} members.")

if __name__ == '__main__':
    reset_members()
