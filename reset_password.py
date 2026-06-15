#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tartib.settings')
django.setup()

from apps.authentication.models import User

try:
    user = User.objects.get(email='admin@tartib.uz')
    user.set_password('admin12345')
    user.save()
    print("✅ Parol o'rnatildi!")
    print("📧 Email: admin@tartib.uz")
    print("🔑 Parol: admin12345")
except User.DoesNotExist:
    print("❌ Admin topilmadi")
