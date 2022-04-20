from django.db import models

# Create your models here.


class Products(models.Model):
    product_name = models.CharField(max_length=255, default="", db_column="ProductName")
    doctor_name = models.CharField(max_length=255, default="", db_column="DoctorName")
    PRODUCT_TYPE = ((1, "Mechanical"), (2, "Biological"))
    product_type = models.IntegerField(
        choices=PRODUCT_TYPE,
        null=True,
        blank=True,
        default=None,
        db_column="ProductType",
    )
    video_link = models.CharField(max_length=255, default="", db_column="VideoLink")
    doctor_image = models.ImageField(
        upload_to="uploads/", db_column="DoctorImage", null=True, blank=True
    )
    country = models.CharField(max_length=255, default="", db_column="Countries")
    description = models.TextField(db_column="Description", default="")

    class Meta:
        db_table = "Products"
