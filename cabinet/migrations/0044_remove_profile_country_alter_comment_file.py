# Generated by Django 5.1.1 on 2024-12-09 10:52

import cabinet.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cabinet', '0043_alter_notification_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='country',
        ),
        migrations.AlterField(
            model_name='comment',
            name='file',
            field=models.FileField(blank=True, upload_to=cabinet.models.user_directory_path_lesson, verbose_name='Файл'),
        ),
    ]
