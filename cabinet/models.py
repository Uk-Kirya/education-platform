import os
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html, strip_tags
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField
import uuid

from losdesign import settings
from .validators import validate_image_format


def user_directory_path_ava(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('user', instance.user.username, filename)


class Profile(models.Model):
    class Meta:
        verbose_name = "Студент"
        verbose_name_plural = "Студенты"

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, verbose_name='Имя')
    phone = models.CharField(max_length=100, blank=True, verbose_name='Телефон')
    photo = models.FileField(upload_to=user_directory_path_ava, blank=True, null=True, verbose_name='Аватарка', validators=[validate_image_format])
    location = models.CharField(max_length=100, blank=True, verbose_name='Адрес')
    bio = models.TextField(max_length=500, blank=True, verbose_name='Коротко о себе')
    is_active = models.BooleanField(default=False, verbose_name='Активный')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')

    def save(self, *args, **kwargs):
        # Проверяем, есть ли уже загруженное фото
        if self.photo:
            try:
                # Получаем текущий объект из базы данных
                current_profile = Profile.objects.get(pk=self.pk)
                # Проверяем, отличается ли новое фото от старого
                if current_profile.photo != self.photo:
                    # Удаляем старое фото
                    if current_profile.photo:
                        if os.path.isfile(current_profile.photo.path):
                            os.remove(current_profile.photo.path)
                else:
                    # Если фото не изменилось, не обрабатываем его
                    super().save(*args, **kwargs)
                    return
            except Profile.DoesNotExist:
                # Если объект не существует, ничего не делаем
                pass

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name or self.user.username


class Page(models.Model):
    class Meta:
        verbose_name = "Страница"
        verbose_name_plural = "Страницы"

    TYPES = [
        ('text', 'Текстовая'),
        ('req', 'Реквизиты'),
        ('help', 'Помощь'),
        ('contacts', 'Контакты'),
    ]

    title = models.CharField(max_length=100, blank=True, verbose_name='Заголовок')
    type = models.CharField(max_length=255, blank=False, null=False, verbose_name='Тип страницы', choices=TYPES)
    text = RichTextUploadingField(blank=True, verbose_name='Текст')
    slug = models.SlugField(max_length=100, blank=True, verbose_name='Slug')

    def safe(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Page, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Module(models.Model):
    class Meta:
        verbose_name = "Модуль"
        verbose_name_plural = "Модули"
        ordering = ['order',]

    title = models.CharField(max_length=255, blank=False, verbose_name='Заголовок')
    picture = models.FileField(upload_to='modules/', blank=True, verbose_name='Обложка')
    text = RichTextUploadingField(blank=True, verbose_name='Текст')
    order = models.IntegerField(blank=True, verbose_name='Порядковый номер')
    status = models.BooleanField(default=True, verbose_name='Активный?')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    slug = models.SlugField(max_length=100, blank=False, verbose_name='Slug')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Module, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ['order',]

    title = models.CharField(max_length=255, blank=False, verbose_name='Заголовок')
    module = models.ForeignKey(Module, on_delete=models.PROTECT, related_name='lessons', verbose_name='Модуль')
    picture = models.FileField(upload_to='lessons/', blank=True, verbose_name='Обложка')
    video = models.CharField(max_length=255, blank=True, verbose_name='Ссылка на видео')
    text = RichTextUploadingField(blank=True, verbose_name='Текст')
    file = models.FileField(upload_to='pdf_files/', blank=True, verbose_name='Презентация PDF')
    status = models.BooleanField(default=True, verbose_name='Активный?')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    order = models.IntegerField(default=0, blank=True, verbose_name='Порядковый номер')
    slug = models.SlugField(max_length=255, blank=False, verbose_name='Slug')
    has_homework = models.BooleanField(default=True, verbose_name='Есть ДЗ?')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Lesson, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


def user_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('homework', instance.user.username, instance.lesson.slug, filename)


class Notification(models.Model):
    class Meta:
        verbose_name = "Домашнее задание"
        verbose_name_plural = "Домашние задания"

    title = models.CharField(max_length=255, blank=False, verbose_name='Заголовок')
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='notifications', verbose_name='Студент')
    lesson = models.ForeignKey(Lesson, on_delete=models.PROTECT, related_name='notifications', verbose_name='Урок')
    text = RichTextUploadingField(blank=True, verbose_name='Текст')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата отправки')
    is_verified = models.BooleanField(default=False, verbose_name='Проверено?')
    is_done = models.BooleanField(default=False, verbose_name='Выполнено?')
    file = models.FileField(upload_to=user_directory_path, blank=True, verbose_name='Файл')

    def save(self, *args, **kwargs):
        if not self.text.startswith('<p>'):
            self.text = format_html('<p>{}</p>', self.text)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


def user_directory_path_lesson(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    lesson_slug = instance.notification.lesson.slug
    return os.path.join('homework', instance.user.username, lesson_slug, filename)


class Comment(models.Model):
    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='comments', verbose_name='Студент')
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='comments', verbose_name='Домашнее задание')
    text = RichTextUploadingField(verbose_name='Текст')
    file = models.FileField(upload_to=user_directory_path_lesson, blank=True, verbose_name='Файл')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_viewed = models.BooleanField(default=False, verbose_name='Просмотрено студентом?')

    def save(self, *args, **kwargs):
        if not self.user:
            self.user = User.objects.get(username='admin')

        # Проверяем, создается ли новый объект
        is_new = not self.pk  # Если у объекта нет pk, значит, он новый

        # Устанавливаем флаг is_viewed, если пользователь не admin
        if self.user.username != 'admin':
            self.is_viewed = True

        # Отправляем письмо, если комментарий создается администратором
        if is_new and self.user.username == 'admin':
            # Получаем пользователя, которому адресован комментарий
            recipient_user = self.notification.user

            # Проверяем, что у пользователя есть email
            if recipient_user.email:
                # Получаем ссылку на урок
                lesson = self.notification.lesson
                if lesson and lesson.module:  # Проверяем, что lesson и module существуют
                    module_slug = lesson.module.slug
                    lesson_slug = lesson.slug
                    lesson_url = reverse('cabinet:lesson', kwargs={'module_slug': module_slug, 'slug': lesson_slug})
                else:
                    lesson_url = None  # Если lesson или module не существуют, ссылка будет None

                # Контекст для шаблона письма
                context = {
                    'name': recipient_user.profile.name if recipient_user.profile else recipient_user.username,
                    'notification_title': self.notification.title,
                    'comment_text': self.text,
                    'lesson_url': f"{settings.PROTOCOL}://{settings.DOMAIN}{lesson_url}" if lesson_url else "Ссылка на урок недоступна",
                    'protocol': settings.PROTOCOL,  # Протокол (http или https)
                    'domain': settings.DOMAIN,  # Домен вашего сайта
                }

                # Рендерим HTML-шаблон
                html_content = render_to_string('comment_notification_email.html', context)

                # Создаем текстовую версию письма
                text_content = strip_tags(html_content)

                # Создаем письмо
                subject = 'Новое сообщение'
                from_email = settings.DEFAULT_FROM_EMAIL
                to_email = recipient_user.email

                msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
                msg.attach_alternative(html_content, "text/html")

                # Отправляем письмо
                msg.send()

        # Форматируем текст комментария
        if not self.text.startswith('<p>'):
            self.text = format_html('<p>{}</p>', self.text)

        # Сохраняем объект
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Комментарий от {self.user} на уведомление {self.notification}"


class Order(models.Model):
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    PAYMENT_STATUS = [
        ('pending', 'В процессе'),
        ('waiting_for_capture', 'Деньги заморожены'),
        ('succeeded', 'Успешно'),
        ('canceled', 'Отменен')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='Студент')
    payment_id = models.CharField(max_length=255, unique=True, verbose_name='ID платежа')
    payment_status = models.CharField(max_length=50, default='pending', verbose_name='Статус', choices=PAYMENT_STATUS)
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма')
    currency = models.CharField(max_length=3, default='RUB', verbose_name='Валюта')

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"
