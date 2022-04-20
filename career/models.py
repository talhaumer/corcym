import datetime

from django.db import models
from django.db.models import Q
from model_utils import Choices

from corcym.settings import DEFAULT_FROM_EMAIL

print(datetime.datetime.now().strftime("%Y-%M-%d"))

ORDER_COLUMN_CHOICES = Choices(
    ("0", "id"),
    ("1", "job_title"),
    ("2", "location"),
    ("3", "description"),
)


class JobPosting(models.Model):
    job_title = models.CharField(max_length=255, db_column="JobTitle")
    location = models.TextField(db_column="Location")
    description = models.TextField(db_column="Description")
    status = models.BooleanField(default=True)
    creation_date = models.DateField(db_column="CreationDate", auto_now=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "JobPosting"


class CandidateDetail(models.Model):
    job = models.ForeignKey(
        JobPosting,
        db_column="JobId",
        related_name="candidate_job",
        on_delete=models.CASCADE,
    )
    first_name = models.CharField(max_length=255, db_column="FirstName")
    last_name = models.CharField(max_length=255, db_column="LastName")

    notes = models.TextField(db_column="Notes", null=True, blank=True)
    email = models.EmailField(unique=False, db_column="Email", help_text="Email Field")
    applying_date = models.DateField(db_column="ApplyingDate", auto_now=True)

    resume = models.FileField(
        upload_to="uploads/", db_column="Resume", null=True, blank=True
    )
    new_file = models.FileField(
        upload_to="uploads/", db_column="NewFile", null=True, blank=True
    )
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "CandidateDetail"


def query_jobs_by_args(query_object, **kwargs):
    print("----------------1------------------")
    try:
        print("--------------2---------------------")
        draw = int(kwargs.get("draw", None)[0])
        length = int(kwargs.get("length", None)[0])
        start = int(kwargs.get("start", None)[0])
        search_value = kwargs.get("search[value]", None)[0]
        order_column = kwargs.get("order[0][column]", None)[0]
        order = kwargs.get("order[0][dir]", None)[0]
        order_column = ORDER_COLUMN_CHOICES[order_column]

        # django orm '-' -> desc
        if order == "desc":
            order_column = "-" + order_column

        queryset = JobPosting.objects.filter(query_object)

        total = queryset.count()
        if search_value:
            queryset = queryset.filter(
                Q(id__icontains=search_value)
                | Q(job_title__icontains=search_value)
                | Q(location__icontains=search_value)
                | Q(description__icontains=search_value)
            )

        count = queryset.count()
        queryset = queryset.order_by(order_column)[start : start + length]
        return {"items": queryset, "count": count, "total": total, "draw": draw}
    except Exception as e:
        print(e)
        return None


def query_candidate_by_args(query_object, **kwargs):
    print("----------------1------------------")
    ORDER_COLUMNS_CHOICES = Choices(
        ("0", "id"),
        ("1", "first_name"),
        ("2", "last_name"),
        ("3", "notes"),
        ("4", "email"),
        ("5", "applying_date"),
        ("6", "us_check"),
        ("7", "resume"),
    )
    try:
        print("--------------2---------------------")
        draw = int(kwargs.get("draw", None)[0])
        length = int(kwargs.get("length", None)[0])
        start = int(kwargs.get("start", None)[0])
        search_value = kwargs.get("search[value]", None)[0]
        order_column = kwargs.get("order[0][column]", None)[0]
        order = kwargs.get("order[0][dir]", None)[0]
        order_column = ORDER_COLUMNS_CHOICES[order_column]

        # django orm '-' -> desc
        if order == "desc":
            order_column = "-" + order_column

        queryset = CandidateDetail.objects.filter(query_object)
        print(queryset)

        total = queryset.count()

        if search_value:
            queryset = queryset.filter(
                Q(id__icontains=search_value)
                | Q(first_name__icontains=search_value)
                | Q(last_name__icontains=search_value)
                | Q(notes__icontains=search_value)
                | Q(email__icontains=search_value)
                | Q(applying_date__icontains=search_value)
                | Q(us_check__icontains=search_value)
                | Q(resume__icontains=search_value)
            )

        count = queryset.count()
        queryset = queryset.order_by(order_column)[start : start + length]
        return {"items": queryset, "count": count, "total": total, "draw": draw}
    except Exception as e:
        print(e)
        return {
            "exception": str(e),
            "items": "0",
            "count": "0",
            "total": "0",
            "draw": "0",
        }


class EmailData(models.Model):
    name = models.CharField(max_length=255, db_column="FirstName")
    message = models.TextField(db_column="Notes", null=True, blank=True)
    email = models.EmailField(unique=False, db_column="Email", help_text="Email Field")
    cv = models.FileField(upload_to="uploads/", db_column="Resume")

    class Meta:
        db_table = "EmailData"
