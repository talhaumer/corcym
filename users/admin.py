from django.contrib import admin
from users.models import UserOperator, User, Role
# Register your models here.

admin.site.register(User)
admin.site.register(UserOperator)
admin.site.register(Role)