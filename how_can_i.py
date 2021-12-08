import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "corcym.settings")
django.setup()

import threading
from django.db import transaction
from support.models import HowCanWeHelpYou 


def add_data_thread():
    # data = Property.objects.all().update(canonical_link=None)

    t1 = threading.Thread(target=add_data())
    t1.start()

def add_data():
    try:
        name = ["Other","Collaborate with us",'Patient card and registration form', 'Product Information', 'Product feedback', 'Report a problem with our devices']
        for each in name:
            with transaction.atomic():
                cnt = {}
                cnt['name'] = each
                print(cnt)
                x = HowCanWeHelpYou.objects.create(**cnt)
    except Exception as e:
        print(e)

add_data_thread()
