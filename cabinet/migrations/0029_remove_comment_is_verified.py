# Generated by Django 5.1.1 on 2024-10-20 20:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cabinet', '0028_remove_notification_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='is_verified',
        ),
    ]
