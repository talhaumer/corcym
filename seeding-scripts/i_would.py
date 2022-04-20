import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "corcym.settings")
django.setup()

import threading

from django.db import transaction

from contact.models import IWouldLikeTo


def add_data_thread():
    # data = Property.objects.all().update(canonical_link=None)

    t1 = threading.Thread(target=add_data())
    t1.start()


def add_data():
    try:
        name = [
            "Receive information on CORCYM courses – please provide details in the box below",
            "Be contacted by a company rep",
            "Speak to a clinician expert - please provide details in the box below",
            "Receive information on other CORCYM educational opportunities - please provide details in the box below",
        ]
        for each in name:
            with transaction.atomic():
                cnt = {}
                cnt["title"] = each
                print(cnt)
                x = IWouldLikeTo.objects.create(**cnt)
    except Exception as e:
        print(e)


add_data_thread()
