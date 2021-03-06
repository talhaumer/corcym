# Generated by Django 3.2.1 on 2021-06-09 10:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Role",
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
                    "name",
                    models.CharField(db_column="Name", max_length=255, unique=True),
                ),
                ("code", models.SlugField(db_column="Code", default="")),
                (
                    "description",
                    models.TextField(blank=True, db_column="Description", null=True),
                ),
                (
                    "access_level",
                    models.IntegerField(
                        choices=[(200, "Operator"), (900, "Super_Admin")],
                        db_column="AccessLevel",
                        default=200,
                    ),
                ),
            ],
            options={
                "db_table": "Role",
            },
        ),
        migrations.CreateModel(
            name="UserOperator",
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
                    "user",
                    models.ForeignKey(
                        db_column="UserId",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="operator_user",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "UserOperator",
            },
        ),
    ]
