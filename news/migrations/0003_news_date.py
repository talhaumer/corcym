# Generated by Django 3.2.1 on 2021-06-09 12:06

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_news_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='date',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2021, 6, 9, 12, 6, 12, 970297, tzinfo=utc)),
            preserve_default=False,
        ),
    ]