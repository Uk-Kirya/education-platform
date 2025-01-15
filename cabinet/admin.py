from django.contrib import admin
from django.utils.html import format_html

from cabinet.models import Profile, Page, Module, Lesson, Notification, Comment, Order


class CommentNotificationInline(admin.TabularInline):
    model = Comment
    extra = 1


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = "get_image", "user", "name", "is_active", "created_at"

    def get_image(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="100">', obj.photo.url)
        else:
            return "Фото не загружено"

    get_image.short_description = 'Фотография'


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = "title", "slug",
    prepopulated_fields = {
        'slug': (
            'title',
        )
    }


class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 0


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = "title", "cover", "slug", "status", "order"
    list_display_links = 'title', 'cover'
    ordering = 'order',
    prepopulated_fields = {
        'slug': (
            'title',
        )
    }
    inlines = [
        LessonInline
    ]

    def cover(self, obj):
        if obj.picture:
            return format_html('<img src="{}" width="200">', obj.picture.url)
        else:
            return "Обложка не загружена"

    cover.short_description = 'Обложка'


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = "title", "cover", "slug", "status", "order", "has_homework"
    list_display_links = 'title', 'cover'
    ordering = 'order',
    prepopulated_fields = {
        'slug': (
            'title',
        )
    }

    def cover(self, obj):
        if obj.picture:
            return format_html('<img src="{}" width="200" alt="">', obj.picture.url)
        else:
            return "Обложка не загружена"

    cover.short_description = 'Обложка'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = "title", "get_name", "created_at", "is_verified", "is_done"
    inlines = [
        CommentNotificationInline
    ]
    search_fields = 'title', 'user__profile__name'

    def get_name(self, obj: Notification) -> str:
        name = Profile.objects.get(user=obj.user)
        return name.name

    get_name.short_description = 'Студент'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = 'user', 'payment_id', 'payment_status', 'payment_date', 'amount', 'currency'
    list_display_links = 'user',
