# Generated by Django 3.2.3 on 2021-06-01 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('support', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailsupport',
            name='message',
            field=models.TextField(db_column='Message'),
        ),
    ]
