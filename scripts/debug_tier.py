import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings')
django.setup()

from accounts.models import User, MembershipTier
from circulation.models import BorrowRecord

def check_john():
    try:
        john = User.objects.get(username='member_john')
        print(f"User: {john.username}")
        print(f"Role: {john.role}")
        print(f"Tier: {john.membership_tier}")
        
        loans = BorrowRecord.objects.filter(user=john, status='ISSUED').count()
        print(f"Active Loans: {loans}")
        
        if john.membership_tier:
             print(f"Max Allowed: {john.membership_tier.max_books}")
        else:
             print("WARNING: No tier assigned!")
             # Fix it now for testing
             basic = MembershipTier.objects.get(name='Basic')
             john.membership_tier = basic
             john.save()
             print("-> Assigned 'Basic' tier to John.")

    except User.DoesNotExist:
        print("User member_john not found.")

if __name__ == '__main__':
    check_john()
