# Generated by Django 5.1.1 on 2024-11-23 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cabinet', '0041_alter_comment_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='is_viewed',
            field=models.BooleanField(default=False, verbose_name='Просмотрено студентом?'),
        ),
    ]