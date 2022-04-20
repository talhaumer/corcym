from django.contrib import admin

from career.models import CandidateDetail, JobPosting

# Register your models here.
admin.site.register(JobPosting)
admin.site.register(CandidateDetail)
