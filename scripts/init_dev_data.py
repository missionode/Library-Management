import json
import os
import sys
import django
from pathlib import Path

# Setup Django Environment
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings')
django.setup()

from accounts.models import User, MembershipTier

def load_secrets():
    try:
        with open(BASE_DIR / 'dev_secrets.json') as f:
            return json.load(f)
    except FileNotFoundError:
        print("dev_secrets.json not found!")
        return {}

def init_tiers():
    tiers = [
        {'name': 'Basic', 'max_books': 2, 'borrow_duration_days': 14, 'subscription_fee': 0.00},
        {'name': 'Premium', 'max_books': 10, 'borrow_duration_days': 30, 'subscription_fee': 19.99},
        {'name': 'Student', 'max_books': 5, 'borrow_duration_days': 21, 'subscription_fee': 5.00},
        {'name': 'Staff', 'max_books': 50, 'borrow_duration_days': 365, 'subscription_fee': 0.00},
    ]
    for t in tiers:
        obj, created = MembershipTier.objects.get_or_create(name=t['name'], defaults=t)
        if created:
            print(f"Created Tier: {t['name']}")

def create_users(users_list, default_role):
    # Fetch default tier based on role
    tier = None
    if default_role == User.Role.MEMBER:
        tier = MembershipTier.objects.get(name='Basic')
    elif default_role in [User.Role.LIBRARIAN, User.Role.ADMIN]:
        tier = MembershipTier.objects.get_or_create(name='Staff')[0]

    for u in users_list:
        if not User.objects.filter(username=u['username']).exists():
            user = User.objects.create_user(
                username=u['username'],
                email=u['email'],
                password=u['password'],
                role=u.get('role', default_role),
                membership_tier=tier
            )
            print(f"Created {default_role}: {u['username']}")
        else:
            print(f"User already exists: {u['username']}")

def init_data():
    secrets = load_secrets()
    
    # Initialize Tiers first
    init_tiers()
    
    # Create Superusers
    staff_tier, _ = MembershipTier.objects.get_or_create(name='Staff', defaults={'max_books': 50, 'borrow_duration_days': 365, 'subscription_fee': 0.00})
    
    for u in secrets.get('superusers', []):
        if not User.objects.filter(username=u['username']).exists():
            User.objects.create_superuser(
                username=u['username'],
                email=u['email'],
                password=u['password'],
                role=User.Role.ADMIN,
                membership_tier=staff_tier
            )
            print(f"Created Admin: {u['username']}")
        else:
            print(f"Admin already exists: {u['username']}")

    # Create Librarians
    create_users(secrets.get('librarians', []), User.Role.LIBRARIAN)

    # Create Members
    create_users(secrets.get('members', []), User.Role.MEMBER)

if __name__ == '__main__':
    init_data()