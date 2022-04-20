from django.contrib import admin

from support.models import EmailSupport, HowCanWeHelpYou, IAm

# Register your models here.

admin.site.register(IAm)
admin.site.register(HowCanWeHelpYou)
admin.site.register(EmailSupport)
