# Generated by Django 5.1.1 on 2024-10-20 20:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cabinet', '0030_notification_is_verified'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='lesson',
        ),
    ]