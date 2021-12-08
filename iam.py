import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "corcym.settings")
django.setup()

import threading
from django.db import transaction
from support.models import IAm 


def add_iam_data_thread():
	# data = Property.objects.all().update(canonical_link=None)

	t1 = threading.Thread(target=iam_data())
	t1.start()

def iam_data():
	try:
		title = ['Patient', 'Heart Surgeon', 'Other Healthcare Professional', 'Media', 'Other']
		for each in title:
			with transaction.atomic():
				cnt = {}
				cnt['title'] = each
				print(cnt)
				x = IAm.objects.create(**cnt)
	except Exception as e:
		print(e)

add_iam_data_thread()
