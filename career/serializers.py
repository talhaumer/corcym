from django.db import transaction
from rest_framework import serializers

from career.models import CandidateDetail, EmailData, JobPosting
from support.serializers import ChoiceField


class CandidateJobSerializer(serializers.ModelSerializer):
    job = serializers.SerializerMethodField(required=False, read_only=True)

    class Meta:
        model = CandidateDetail

    def get_job(self, obj):
        try:
            return obj.job.job_title
        except:
            return None


class CandidateNewFieldSerializer(serializers.ModelSerializer):
    new_file = serializers.FileField(required=True)

    class Meta:
        model = CandidateDetail
        fields = ["new_file"]

    def update(self, instance, validated_data):
        instance.new_file = validated_data.get("new_file", instance.new_file)
        instance.save()
        return instance


class CandidateDetailSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    resume = serializers.FileField(required=False)
    job = serializers.SerializerMethodField(required=False, read_only=True)
    job_id = serializers.IntegerField(required=True)
    # us_check = ChoiceField(choices = CandidateDetail.US_CHECK)

    class Meta:
        model = CandidateDetail
        fields = (
            "id",
            "job_id",
            "job",
            "first_name",
            "last_name",
            "email",
            "notes",
            "resume",
        )

    def create(self, validated_data):
        return CandidateDetail.objects.create(**validated_data)

    def get_job(self, obj):
        try:

            return {"job_title": obj.job.job_title, "location": obj.job.location}
        except:
            return None


class JobPostingSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    job_title = serializers.CharField(required=True)
    location = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    status = serializers.BooleanField(read_only=True)

    class Meta:
        model = JobPosting
        fields = ["id", "job_title", "description", "location", "status"]

    def create(self, validated_data):
        job_posting = JobPosting.objects.create(**validated_data)
        return job_posting

    def update(self, instance, validated_data):
        instance.job_title = validated_data.get("job_title", instance.job_title)
        instance.location = validated_data.get("location", instance.location)
        instance.description = validated_data.get("description", instance.description)
        instance.save()
        return instance


class EmailDataSerializer(serializers.ModelSerializer):

    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    message = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    cv = serializers.FileField(required=True)

    class Meta:
        model = EmailData
        fields = ("id", "name", "email", "message", "cv")

    def create(self, validated_data):
        return EmailData.objects.create(**validated_data)


class JobListingSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    job_title = serializers.CharField(read_only=True)

    class Meta:
        model = JobPosting
        fields = ["id", "job_title"]


class JobLocationSerializer(serializers.ModelSerializer):
    location = serializers.CharField(read_only=True)

    class Meta:
        model = JobPosting
        fields = ["location"]


class JobTitleSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(read_only=True)

    class Meta:
        model = JobPosting
        fields = ["job_title"]


class JobCityListingSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    job_title = serializers.CharField(read_only=True)
    location = serializers.CharField(read_only=True)

    class Meta:
        model = JobPosting
        fields = ["id", "job_title", "location"]
