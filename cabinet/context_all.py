from django.http import HttpRequest, HttpResponse

from .models import Comment, Notification, Module, Lesson, Order, Page, Profile


def context_all(request: HttpRequest) -> dict:
    new_comments = 0
    comments_header = ''

    if request.user.is_authenticated:
        notification = Notification.objects.filter(user=request.user)
        comments_header = Comment.objects.filter(notification__in=notification).order_by('-created_at')
        new_comments = Comment.objects.filter(is_viewed=False, notification__in=notification).count()

    return {
        'new_comments': new_comments,
        'comments_header': comments_header,
    }


def admin_stats(request):
    if request.path.startswith('/admin/'):
        return {
            'modules_count': Module.objects.count(),
            'lessons_count': Lesson.objects.count(),
            'orders_count': Order.objects.count(),
            'pages_count': Page.objects.count(),
            'students_count': Profile.objects.count(),
            'hw_count': Notification.objects.count()
        }
    return {}
