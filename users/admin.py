from django.contrib import admin

from users.models import Role, User, UserOperator

# Register your models here.

admin.site.register(User)
admin.site.register(UserOperator)
admin.site.register(Role)
