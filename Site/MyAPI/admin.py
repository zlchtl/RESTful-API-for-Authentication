from django.contrib import admin
from .models import User, RefreshToken

admin.site.register(User)
admin.site.register(RefreshToken)
