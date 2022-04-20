from django.db import models
from django.db.models import Q
from django.utils.text import slugify
from model_utils import Choices


# Create your models here.
class IAm(models.Model):
    title = models.CharField(db_column="Title", max_length=255)
    title_code = models.SlugField(max_length=255, unique=True, default="")

    class Meta:
        db_table = "IAm"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        try:
            if not self.pk:
                self.title_code = slugify(self.title)
            super().save()
        except Exception:
            raise


class HowCanWeHelpYou(models.Model):
    name = models.CharField(db_column="Title", max_length=255)
    name_code = models.SlugField(max_length=255, unique=True, default="")

    class Meta:
        db_table = "HowCanWeHelpYou"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        try:
            if not self.pk:
                self.name_code = slugify(self.name)
            super().save()
        except Exception:
            raise


class EmailSupport(models.Model):
    first_name = models.CharField(db_column="FirstName", max_length=255)
    last_name = models.CharField(db_column="LastName", max_length=255)
    i_am = models.ForeignKey(
        IAm, db_column="IAmId", related_name="i_am_support", on_delete=models.CASCADE
    )
    city = models.CharField(db_column="City", max_length=255, null=True, blank=True)
    country = models.CharField(db_column="Country", max_length=255)
    message = models.TextField(db_column="Message")
    email = models.EmailField(unique=False, db_column="Email", help_text="Email Field")
    state = models.CharField(db_column="State", max_length=255, null=True, blank=True)
    phone_number = models.CharField(
        db_column="PhoneNumber", max_length=255, null=True, blank=True
    )
    how_can_we_help = models.ForeignKey(
        HowCanWeHelpYou,
        db_column="HowCanWeHelpYouId",
        related_name="email_support_how_can_we_help",
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = "EmailSupport"


class Donation(models.Model):
    country = models.CharField(db_column="Country", max_length=255)
    applicant_organization = models.CharField(
        db_column="ApplicantOrganizationName", max_length=255
    )
    name = models.CharField(
        db_column="NameInLocalLanguage", max_length=255, null=True, blank=True
    )
    email = models.EmailField(unique=False, db_column="Email", help_text="Email Field")
    applicant_organization_address = models.TextField(
        db_column="ApplicantOrganizationAddress"
    )
    organization_type = models.CharField(db_column="OrganizationType", max_length=255)
    organization_tax_id = models.CharField(
        db_column="OrganizationTaxId", max_length=255, null=True, blank=True
    )
    website = models.TextField(db_column="Website", null=True, blank=True)
    w9_form = models.FileField(
        upload_to="uploads/", db_column="W-9Form", null=True, blank=True
    )
    TYPE_OF_REQUEST = (
        (1, "Educational Grant"),
        (2, "Research Grant"),
        (3, "Third party educational events"),
        (4, "Charitable Donation"),
    )
    type_of_request = models.IntegerField(
        choices=TYPE_OF_REQUEST, db_column="ResearchGrant", null=True, blank=True
    )
    notes = models.TextField(db_column="Notes", null=True, blank=True)

    class Meta:
        db_table = "Donation"


def query_support_email_by_args(query_object, **kwargs):
    ORDER_COLUMN_CHOICES = Choices(
        ("0", "id"),
        ("1", "first_name"),
        ("2", "last_name"),
        ("3", "i_am"),
        ("4", "city"),
        ("5", "country"),
        ("6", "message"),
        ("7", "email"),
        ("8", "state"),
        ("9", "phone_number"),
        ("10", "how_can_we_help"),
    )
    try:
        print("---------------query_news_by_args---------------------------")
        draw = int(kwargs.get("draw", 10)[0])
        length = int(kwargs.get("length", 0)[0])
        start = int(kwargs.get("start", 0)[0])
        search_value = kwargs.get("search[value]", None)[0]
        order_column = kwargs.get("order[0][column]", None)[0]
        order = kwargs.get("order[0][dir]", None)[0]

        order_column = ORDER_COLUMN_CHOICES[order_column]

        # django orm '-' -> desc
        if order == "desc":
            order_column = "-" + order_column
        queryset = EmailSupport.objects.filter(query_object)
        total = queryset.count()

        if search_value:
            queryset = queryset.filter(
                Q(id__icontains=search_value)
                | Q(first_name__icontains=search_value)
                | Q(last_name__icontains=search_value)
                | Q(i_am__icontains=search_value)
                | Q(city__icontains=search_value)
                | Q(message__icontains=search_value)
                | Q(email__icontains=search_value)
                | Q(state__icontains=search_value)
                | Q(phone_number__icontains=search_value)
                | Q(how_can_we_help__icontains=search_value)
            )

        count = queryset.count()
        queryset = queryset.order_by(order_column)[start : start + length]
        return {"items": queryset, "count": count, "total": total, "draw": draw}
    except Exception as e:
        print("Exception")
        print(e)
        return {"items": 0, "count": 0, "total": 0, "draw": 0}


def query_donation_email_by_args(query_object, **kwargs):
    ORDER_COLUMN_CHOICES = Choices(
        ("0", "id"),
        ("1", "country"),
        ("2", "applicant_organization"),
        ("3", "name"),
        ("4", "applicant_organization_address"),
        ("5", "organization_type"),
        ("6", "organization_tax_id"),
        ("7", "website"),
        ("8", "w9_form"),
    )
    try:

        draw = int(kwargs.get("draw", 10)[0])
        length = int(kwargs.get("length", 0)[0])
        start = int(kwargs.get("start", 0)[0])
        search_value = kwargs.get("search[value]", None)[0]
        order_column = kwargs.get("order[0][column]", None)[0]
        order = kwargs.get("order[0][dir]", None)[0]

        order_column = ORDER_COLUMN_CHOICES[order_column]

        if order == "desc":
            order_column = "-" + order_column
        queryset = Donation.objects.filter(query_object)
        total = queryset.count()

        if search_value:
            queryset = queryset.filter(
                Q(id__icontains=search_value)
                | Q(country__icontains=search_value)
                | Q(applicant_organization__icontains=search_value)
                | Q(name__icontains=search_value)
                | Q(applicant_organization_address__icontains=search_value)
                | Q(organization_type__icontains=search_value)
                | Q(organization_tax_id__icontains=search_value)
                | Q(website__icontains=search_value)
                | Q(w9_form__icontains=search_value)
            )

        count = queryset.count()
        queryset = queryset.order_by(order_column)[start : start + length]
        return {"items": queryset, "count": count, "total": total, "draw": draw}
    except Exception as e:
        print("Exception")
        print(e)
        return {"items": 0, "count": 0, "total": 0, "draw": 0}
