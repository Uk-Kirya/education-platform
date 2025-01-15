# Generated by Django 5.1.1 on 2024-10-16 18:35

import ckeditor_uploader.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cabinet', '0012_module'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Заголовок')),
                ('picture', models.FileField(blank=True, upload_to='lessons/', verbose_name='Обложка')),
                ('video', models.CharField(blank=True, max_length=255, verbose_name='Ссылка на видео')),
                ('text', ckeditor_uploader.fields.RichTextUploadingField(blank=True, verbose_name='Текст')),
                ('file', models.FileField(blank=True, upload_to='pdf_files/', verbose_name='Презентация PDF')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('slug', models.SlugField(max_length=255, verbose_name='Slug')),
            ],
            options={
                'verbose_name': ('Урок',),
                'verbose_name_plural': 'Уроки',
            },
        ),
        migrations.AlterField(
            model_name='module',
            name='slug',
            field=models.SlugField(max_length=100, verbose_name='Slug'),
        ),
    ]