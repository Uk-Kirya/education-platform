# Generated by Django 5.1.1 on 2024-10-19 21:46

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cabinet', '0020_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Дата отправки'),
            preserve_default=False,
        ),
    ]
