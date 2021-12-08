import os
import django
from django.utils.text import slugify

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "corcym.settings")
django.setup()

import threading
from django.db import transaction
from users.models import AccessLevel, Role

def add_roles():
    roles = AccessLevel.DICT
    for acl, role in roles.items():
        role_object = Role.objects.filter(name=role, access_level=acl)
        # created = Group.objects.get_or_create(name=role)
        
        if role_object.exists():
            print(f'{role} exists')
            continue
        else:
            r = Role(name=role, access_level=acl)
            r.save()
            print(f'{role} newly added.')
    print('All above roles have been added/updated successfully.')


if __name__ == "__main__":
    add_roles()