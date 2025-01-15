from django.contrib.auth.views import (
    PasswordResetCompleteView,
    PasswordResetDoneView,
)
from django.urls import path, reverse_lazy

from .views import (
    cabinet,
    logout_view,
    registration_view,
    ProfileView,
    login_view,
    ResetPass,
    PageView,
    ConfirmPass,
    ModuleDetailView,
    LessonDetailView,
    Notifications,
    login_view_new_password,
    has_viewed,
    change_password,
    mark_comment_as_viewed,
    create_payment,
    was_paid_for,
)

app_name = 'cabinet'

urlpatterns = [
    path('', login_view, name="home"),
    path('cabinet/', cabinet, name="cabinet"),
    path('cabinet/create-payment/', create_payment, name='create_payment'),
    path('cabinet/was-paid-for/', was_paid_for, name='was_paid_for'),
    path('cabinet/notifications/', Notifications.as_view(), name="notifications"),
    path('cabinet/notifications/has-viewed', has_viewed, name="has_viewed"),
    path('logout/', logout_view, name='logout'),
    path('registration/', registration_view, name='registration'),
    path('<slug:slug>/', PageView.as_view(), name="text_page"),
    path('cabinet/profile/<str:username>', ProfileView.as_view(), name='profile'),
    path('cabinet/profile/<str:username>/change-password/', change_password, name='change_password'),
    path('cabinet/<str:slug>', ModuleDetailView.as_view(), name="module"),
    path('cabinet/<str:module_slug>/<str:slug>', LessonDetailView.as_view(), name="lesson"),
    path('cabinet/mark_comment_as_viewed/<int:comment_id>/', mark_comment_as_viewed, name='mark_comment_as_viewed'),

    path('auth/password_reset/', ResetPass.as_view(), name='password_reset'),
    path('auth/password_reset/done/', PasswordResetDoneView.as_view(template_name='users/management/password-reset-done.html'), name='password_reset_done'),
    path('auth/reset/<uidb64>/<token>/', ConfirmPass.as_view(), name='password_reset_confirm'),
    path('auth/reset/done/', login_view_new_password, name='password_reset_complete'),
]
