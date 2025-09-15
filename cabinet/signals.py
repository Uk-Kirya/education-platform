from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import Comment


@receiver(post_save, sender=Comment)
def send_comment_notification(sender, instance, created, **kwargs):
    if created and instance.user.username != 'admin':
        # Получаем данные для шаблона
        context = {
            'name': instance.user.profile.name,  # Предполагаем, что у пользователя есть профиль с именем
            'notification_title': instance.notification.title,
            'comment_text': instance.text,
            'protocol': 'https',  # или 'http' в зависимости от вашего сервера
            'domain': settings.DOMAIN,  # Домен вашего сайта (должен быть указан в settings.py)
        }

        # Рендерим HTML-шаблон
        html_content = render_to_string('comment_notification_email.html', context)

        # Создаем текстовую версию письма (для клиентов, которые не поддерживают HTML)
        text_content = strip_tags(html_content)

        # Создаем письмо
        subject = 'Новое сообщение'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = instance.user.email

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, "text/html")

        # Отправляем письмо
        msg.send()
