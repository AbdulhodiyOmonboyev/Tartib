from apps.authentication.models import User
user = User.objects.get(email='admin@tartib.uz')
user.set_password('admin12345')
user.save()
print(f"✅ Parol o'rnatildi: admin12345")
print(f"Email: admin@tartib.uz")
