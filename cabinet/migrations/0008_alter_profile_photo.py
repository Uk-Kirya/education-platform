# Generated by Django 5.1.1 on 2024-09-15 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cabinet', '0007_alter_profile_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='photo',
            field=models.FileField(blank=True, upload_to='users/', verbose_name='Аватарка'),
        ),
    ]
