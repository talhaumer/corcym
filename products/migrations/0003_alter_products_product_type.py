# Generated by Django 3.2.1 on 2021-07-13 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0002_alter_products_product_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="products",
            name="product_type",
            field=models.IntegerField(
                blank=True,
                choices=[(1, "Mechanical"), (2, "Biological")],
                db_column="ProductType",
                default=1,
                null=True,
            ),
        ),
    ]
