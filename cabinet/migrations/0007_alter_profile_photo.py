# Generated by Django 5.1.1 on 2024-09-15 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cabinet', '0006_remove_profile_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='photo',
            field=models.ImageField(blank=True, upload_to='users/', verbose_name='Аватарка'),
        ),
    ]