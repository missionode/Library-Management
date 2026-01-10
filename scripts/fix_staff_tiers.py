import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings')
django.setup()

from accounts.models import User, MembershipTier

def fix_staff_tiers():
    staff_tier, _ = MembershipTier.objects.get_or_create(
        name='Staff', 
        defaults={'max_books': 50, 'borrow_duration_days': 365, 'subscription_fee': 0.00}
    )
    
    # Update Admins and Librarians who have no tier
    users = User.objects.filter(role__in=['ADMIN', 'LIBRARIAN'], membership_tier__isnull=True)
    count = users.count()
    
    for u in users:
        u.membership_tier = staff_tier
        u.save()
        print(f"Assigned 'Staff' tier to {u.username}")
        
    print(f"Updated {count} users.")

if __name__ == '__main__':
    fix_staff_tiers()
