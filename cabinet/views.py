import random
import json
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView
import math

from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.utils.html import strip_tags
from django.views import View
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, DetailView, FormView
import re

from .forms import HomeWorkSendForm, CommentForm
from .models import Profile, Page, Module, Lesson, Notification, Comment, Order

import uuid
from yookassa import Configuration, Payment
Configuration.account_id = settings.ACCOUNT_ID_YOOKASSA
Configuration.secret_key = settings.SECRET_KEY_YOOKASSA


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('cabinet/')

        context = {
            'message': False
        }
        return render(request, 'main.html', context=context)

    email = request.POST['email']
    password = request.POST['password']

    try:
        user = User.objects.get(email=email)
    except:
        return render(request, 'main.html', {'message': 'Введенный логин не найден'})

    user = authenticate(request, username=user.username, password=password)

    if user is not None:
        login(request, user)
        next_url = request.GET.get('next', 'cabinet:cabinet')
        return redirect(next_url)

    context = {
        'message': 'Введенный пароль неверный'
    }
    return render(request, 'main.html', context=context)


@login_required
def cabinet(request: HttpRequest) -> HttpResponse:
    modules = Module.objects.filter(status=True)
    lessons = Lesson.objects.filter(has_homework=True)
    lesson_done = Notification.objects.filter(is_done=True, user=request.user)

    count_lessons_percent = (len(lesson_done) / len(lessons)) * 100

    lessons_done_count = {}
    lessons_with_homework = {}
    for module in modules:
        lessons_done_count[module.id] = lesson_done.filter(lesson__module=module).count()
        lessons_with_homework[module.id] = lessons.filter(module=module).count()

    greetings = [
        'Сегодня прекрасный день, чтобы узнать что-то новое!',
        'Ну что, покорим сегодня новые вершины знаний?',
        'Долой тоску и уныние — мир дизайна ждет тебя!',
        'Сегодня ты станешь ближе к своим мечтам и целям!',
        'Смелость и упорство — ключ к успеху!'
    ]

    greeting = random.choice(greetings)

    # Получаем последний платеж пользователя
    last_order = Order.objects.filter(user=request.user).order_by('-payment_date').first()
    payment_status = last_order.payment_status if last_order else None

    context = {
        'user': request.user,
        'modules': modules,
        'lesson_done': lesson_done,
        'lessons_done_count': lessons_done_count,
        'lessons': lessons,
        'lessons_with_homework': lessons_with_homework,
        'count_lessons_percent': math.floor(count_lessons_percent),
        'greeting': greeting,
        'payment_status': payment_status,
    }
    return render(request, 'cabinet.html', context=context)


@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect('cabinet:home')


def registration_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(email=email).exists():
            context = {
                'name_value': name,
                'password_value': password,
                'message': 'Пользователь с таким E-mail уже существует'
            }
            return render(request, 'registration.html', context=context)

        if len(password) < 8:
            context = {
                'name_value': name,
                'email_value': email,
                'message': 'Пароль должен быть не меньше 8-ми символов'
            }
            return render(request, 'registration.html', context=context)

        if not re.search(r'[a-zA-Z]', password) or not re.search(r'[0-9]', password):
            context = {
                'name_value': name,
                'email_value': email,
                'message': 'Пароль должен содержать буквы и цифры'
            }
            return render(request, 'registration.html', context=context)

        try:
            username = email.split('@')[0]
            user = User.objects.create_user(username=username, password=password, email=email)
            Profile.objects.create(user=user, name=name)
        except Exception as e:
            return render(request, 'registration.html', {'message': e})

        context = {
            'name': name,
            'email': email,
            'password': password,
            'protocol': request.scheme,
            'domain': request.get_host(),
        }
        html_message = render_to_string('registration_success_email.html', context)
        plain_message = strip_tags(html_message)
        send_mail(
            'Успешная регистрация',
            plain_message,
            settings.EMAIL_HOST_USER,
            [email],
            html_message=html_message,
        )

        user = authenticate(
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('/cabinet/')

        return render(request, 'registration.html', {'message': 'Ошибка аутентификации'})

    context = {
        'name_value': '',
        'email_value': '',
        'password_value': '',
        'message': False
    }
    return render(request, 'registration.html', context=context)


class ResetPass(PasswordResetView):
    template_name = 'users/management/password-reset.html'
    email_template_name = 'users/management/password_reset_email.html'
    html_email_template_name = 'users/management/password_reset_email.html'
    success_url = '/auth/password_reset/done/'

    def form_valid(self, form):
        email = form.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            messages.error(self.request, 'Пользователь с таким E-mail не существует')
            return render(self.request, self.template_name, {'form': form})
        return super().form_valid(form)


class ConfirmPass(PasswordResetConfirmView):
    template_name = 'users/management/password-confirm.html'
    success_url = '/cabinet/'

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        password = request.POST.get('new_password1')
        password2 = request.POST.get('new_password2')

        if password2 != password:
            messages.error(request, 'Пароли не совпадают')
            return HttpResponseRedirect(f'/auth/reset/{kwargs["uidb64"]}/{kwargs["token"]}/')

        if form.is_valid():
            if len(password) < 8:
                messages.error(request, 'Пароль должен быть не меньше 8 символов')
                return HttpResponseRedirect(f'/auth/reset/{kwargs["uidb64"]}/{kwargs["token"]}/')

            if not re.search(r'[a-zA-Z]', password) or not re.search(r'[0-9]', password):
                messages.error(request, 'Пароль должен содержать буквы и цифры')
                return HttpResponseRedirect(f'/auth/reset/{kwargs["uidb64"]}/{kwargs["token"]}/')

            return self.form_valid(form)

        return self.form_invalid(form)


def login_view_new_password(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('cabinet/')

        return render(request, 'users/management/password-reset-complete.html')

    email = request.POST['email']
    password = request.POST['password']

    try:
        user = User.objects.get(email=email)
    except:
        return render(request, 'main.html', {'message': 'Введенный логин не найден'})

    user = authenticate(request, username=user.username, password=password)

    if user is not None:
        login(request, user)
        return redirect('cabinet/')

    return render(request, 'users/management/password-reset-complete.html', {'message': 'Неверно введен логин или пароль'})


class ProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    fields = "name", "phone", "photo", "location", "bio"
    template_name = 'profile.html'

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        return get_object_or_404(Profile, user__username=username)

    def get_success_url(self):
        return reverse("cabinet:profile", kwargs={"username": self.object.user.username})

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, 'Профиль обновлен 👌🏻')
            return response
        except ValidationError as e:
            messages.error(self.request, e.message)
            print(f"Validation error: {e.message}")  # Отладочное сообщение
            return self.form_invalid(form)


def change_password(request: HttpRequest, username: str) -> HttpResponse:
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        next_url = request.path

        if not check_password(old_password, request.user.password):
            messages.error(request, 'Текущий пароль неверный!')
            return redirect(next_url)
        elif new_password1 != new_password2:
            messages.error(request, 'Новые пароли не совпадают!')
            return redirect(next_url)
        elif len(new_password1) < 8:
            messages.error(request, 'Пароль должен быть не меньше 8-ми символов')
            return redirect(next_url)

        if not re.search(r'[a-zA-Z]', new_password1) or not re.search(r'[0-9]', new_password1):
            messages.error(request, 'Пароль должен содержать буквы и цифры')
            return redirect(next_url)
        else:
            request.user.set_password(new_password1)
            request.user.save()

            update_session_auth_hash(request, request.user)

            messages.success(request, 'Пароль успешно изменен!')
            return redirect('cabinet:profile', username=request.user.username)

    return redirect('cabinet:profile', username=request.user.username)


class PageView(View):
    def get(self, request: HttpRequest, slug: str) -> HttpResponse:
        page = get_object_or_404(Page, slug=slug)
        context = {
            "page": page,
        }
        return render(request, 'text_page.html', context=context)


class ModuleDetailView(LoginRequiredMixin, DetailView):
    template_name = 'module.html'
    model = Module
    context_object_name = 'module'

    def get(self, request, *args, **kwargs):
        if not self.request.user.profile.is_active:
            return redirect('cabinet:home')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        lessons = self.object.lessons.filter(status=True)
        context['lessons'] = lessons

        user = self.request.user
        notifications_is_done = Notification.objects.filter(lesson__in=lessons, is_done=True, user=user)
        context['notifications_is_done'] = notifications_is_done

        lesson_done = {
            notification.lesson.id for notification in Notification.objects.filter(lesson__in=lessons, is_done=True, user=user)
        }
        context['lesson_done'] = lesson_done

        lesson_paused = {
            notification.lesson.id for notification in Notification.objects.filter(lesson__in=lessons, user=user)
        }
        context['lesson_paused'] = lesson_paused

        lessons_with_hw = self.object.lessons.filter(status=True, has_homework=True)
        if len(notifications_is_done) > 0:
            lessons_percent = (len(notifications_is_done) / len(lessons_with_hw)) * 100
        else:
            lessons_percent = False
        context['lessons_percent'] = math.floor(lessons_percent)

        lessons_with_hm = self.object.lessons.filter(status=True, has_homework=True)
        if lessons_with_hm is False:
            lessons_with_hm = False
        context['lessons_with_hm'] = lessons_with_hm

        return context


class LessonDetailView(LoginRequiredMixin, DetailView):
    template_name = 'lesson.html'
    model = Lesson
    context_object_name = 'lesson'

    def get(self, request, *args, **kwargs):
        if not self.request.user.profile.is_active:
            return redirect('cabinet:home')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['notifications'] = Notification.objects.filter(lesson=self.object, user=user)

        if self.object.has_homework:
            context['form'] = HomeWorkSendForm()

        context['comment_form'] = CommentForm()
        context['comments'] = Comment.objects.filter(notification__lesson=self.object)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if 'homework_submit' in request.POST:
            form = HomeWorkSendForm(request.POST, request.FILES)
            file = request.FILES.get('file')

            if file and file.size > settings.MAX_FILE_SIZE:
                messages.error(request, 'Размер файла не должен превышать 10 МБ.')
                return HttpResponseRedirect(self.request.path)

            if form.is_valid():
                notification = form.save(commit=False)
                notification.lesson = self.object
                notification.user = request.user
                notification.text = form.cleaned_data['text']
                notification.title = f"{self.object.title}"
                notification.file = file
                notification.save()
                messages.success(request, 'Домашнее задание отправлено успешно!')
                return HttpResponseRedirect(self.request.path)

        elif 'comment_submit' in request.POST:
            comment_form = CommentForm(request.POST, request.FILES)
            file = request.FILES.get('file')

            if file and file.size > settings.MAX_FILE_SIZE:
                messages.error(request, 'Размер файла не должен превышать 10 МБ.')
                return HttpResponseRedirect(self.request.path)

            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                notification = Notification.objects.get(id=request.POST.get('notification_id'))
                notification.is_verified = False
                comment.user = request.user
                comment.text = comment_form.cleaned_data['text']
                comment.notification = notification
                comment.file = file
                comment.save()
                notification.save()
                messages.success(request, 'Ответ опубликован!')
                return HttpResponseRedirect(self.request.path)

        return HttpResponseRedirect(self.request.path)


class Notifications(LoginRequiredMixin, TemplateView):
    template_name = 'notifications.html'

    def get(self, request, *args, **kwargs):
        if not self.request.user.profile.is_active:
            return redirect('cabinet:home')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        modules = Module.objects.all()
        context['modules'] = modules

        lessons = Lesson.objects.filter(module__in=modules)
        context['lessons'] = lessons

        notifications = Notification.objects.filter(lesson__in=lessons).order_by('-created_at')
        context['notifications'] = notifications

        comments = Comment.objects.filter(notification__in=notifications)
        context['comments'] = comments

        return context


@login_required
def has_viewed(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        comment_id = request.POST.get('comment_id')
        next_url = request.POST.get('next_url')
        comment = Comment.objects.filter(id=comment_id).first()
        comment.is_viewed = True
        comment.save()

        messages.success(request, 'Статус комментария изменен')
        return redirect(next_url)


def mark_comment_as_viewed(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    comment.is_viewed = True
    comment.save()
    return redirect('cabinet:lesson', module_slug=comment.notification.lesson.module.slug, slug=comment.notification.lesson.slug)


@login_required
def create_payment(request: HttpRequest) -> HttpResponse:
    user = request.user

    payment = Payment.create({
        "amount": {
            "value": "20000.00",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://go.losdesign.ru/cabinet/was-paid-for/"
        },
        "capture": True,
        "description": f"Заказ №{user.id}"
    }, uuid.uuid4())

    Order.objects.create(
        user=user,
        payment_id=payment.id,
        amount=payment.amount.value,
        currency=payment.amount.currency,
        payment_status=payment.status
    )

    confirmation_url = payment.confirmation.confirmation_url
    return redirect(confirmation_url)


@login_required
def was_paid_for(request: HttpRequest) -> HttpResponse:
    user = request.user

    try:
        order = Order.objects.filter(user=user).latest('payment_date')
    except Order.DoesNotExist:
        return HttpResponse(status=404)  # Заказ не найден

    payment_id = order.payment_id

    try:
        payment = Payment.find_one(payment_id)
    except Exception as e:
        return HttpResponse(status=500, content=f"Error fetching payment: {str(e)}")

    if payment.status == 'succeeded':
        user.profile.is_active = True
        user.profile.save()

        order.payment_status = payment.status
        order.save()

        subject = f"Успешная оплата заказа №{order.id}"
        message = render_to_string('payment_success_email.html', {
            'user': user,
            'order': order,
            'payment': payment,
        })
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], html_message=message)

    return redirect('cabinet:cabinet')

