# Generated by Django 5.1.1 on 2024-10-16 18:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cabinet', '0016_alter_lesson_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='order',
            field=models.IntegerField(blank=True, default=0, verbose_name='Порядковый номер'),
            preserve_default=False,
        ),
    ]
