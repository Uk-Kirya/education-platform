# Generated by Django 5.1.1 on 2024-10-16 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cabinet', '0015_alter_lesson_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='status',
            field=models.BooleanField(default=True, verbose_name='Активный?'),
        ),
    ]
