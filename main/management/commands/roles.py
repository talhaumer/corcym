from django.core.management import BaseCommand

from users.models import AccessLevel, Role
from django.contrib.auth.models import Group
from django.contrib.auth.models import Group, Permission


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


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            add_roles()
        except Exception as e:
            print(e)