# Generated by Django 3.2.1 on 2021-06-10 08:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20210609_0437'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='useroperator',
            name='is_active',
        ),
    ]