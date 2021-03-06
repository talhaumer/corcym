# Generated by Django 3.2.1 on 2021-07-13 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Products",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "product_name",
                    models.CharField(
                        db_column="ProductName", default="", max_length=255
                    ),
                ),
                (
                    "doctor_name",
                    models.CharField(
                        db_column="DoctorName", default="", max_length=255
                    ),
                ),
                (
                    "product_type",
                    models.CharField(
                        db_column="ProductType", default="", max_length=255
                    ),
                ),
                (
                    "video_link",
                    models.CharField(db_column="VideoLink", default="", max_length=255),
                ),
                (
                    "doctor_image",
                    models.ImageField(
                        blank=True,
                        db_column="DoctorImage",
                        null=True,
                        upload_to="uploads/",
                    ),
                ),
                (
                    "country",
                    models.CharField(db_column="Countries", default="", max_length=255),
                ),
                ("description", models.TextField(db_column="Description", default="")),
            ],
            options={
                "db_table": "Products",
            },
        ),
    ]
