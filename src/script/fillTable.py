from django.contrib.auth.models import User

print(" ------------- DÉBUT -------------")
User.objects.create_user(username="user", password="0123")
print(" ------------- FIN -------------")