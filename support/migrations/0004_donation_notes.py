# Generated by Django 3.2.1 on 2021-07-06 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('support', '0003_donation_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='notes',
            field=models.TextField(blank=True, db_column='Notes', null=True),
        ),
    ]
