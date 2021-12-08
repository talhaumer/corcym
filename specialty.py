import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "corcym.settings")
django.setup()

import threading
from django.db import transaction
from contact.models import Specialty 


def add_data_thread():
    # data = Property.objects.all().update(canonical_link=None)

    t1 = threading.Thread(target=add_data())
    t1.start()

def add_data():
    try:
        name = ['Surgeon', 'Anesthesiologist', 'Nurse', 'Perfusionist', 'Other']
        for each in name:
            with transaction.atomic():
                cnt = {}
                cnt['title'] = each
                print(cnt)
                x = Specialty.objects.create(**cnt)
    except Exception as e:
        print(e)

add_data_thread()
