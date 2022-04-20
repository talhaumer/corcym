from django.core.management import BaseCommand

from users.models import AccessLevel, Role


def add_roles():
    roles = AccessLevel.DICT
    for acl, role in roles.items():
        role_object = Role.objects.filter(name=role, access_level=acl)

        if role_object.exists():
            print(f"{role} exists")
            continue
        else:
            r = Role(name=role, access_level=acl)
            r.save()
            print(f"{role} newly added.")
    print("All above roles have been added/updated successfully.")


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            add_roles()
        except Exception as e:
            print(e)
