from django.contrib import admin
from django.utils.html import format_html

from cabinet.models import Profile, Page, Module, Lesson, Notification, Comment, Order


class CommentNotificationInline(admin.TabularInline):
    model = Comment
    extra = 1


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        "get_image",
        "name",
        "is_active",
        "created_at"
    ]

    list_filter = [
        'is_active',
        'created_at',
    ]

    list_per_page = 50

    search_fields = [
        'name',
    ]

    readonly_fields = [
        'user'
    ]

    def get_image(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="100">', obj.photo.url)
        else:
            return "Фото не загружено"

    get_image.short_description = 'Фотография'

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)

        # скрываем user при редактировании
        if obj and 'user' in fields:
            fields.remove('user')

        return fields


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = [
        "title",
    ]

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
    list_display = [
        "title",
        "cover",
        "count_lessons",
        "status",
        "order"
    ]

    list_per_page = 50

    list_display_links = [
        'title',
        'cover'
    ]

    list_filter = [
        "status",
    ]

    list_editable = [
        'status',
        'order'
    ]

    ordering = 'order',

    prepopulated_fields = {
        'slug': (
            'title',
        )
    }

    inlines = [
        LessonInline
    ]

    def count_lessons(self, obj):
        return obj.lessons.count()

    count_lessons.short_description = 'Уроки'

    def cover(self, obj):
        if obj.picture:
            return format_html('<img src="{}" width="100">', obj.picture.url)
        else:
            return "Обложка не загружена"

    cover.short_description = 'Обложка'


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "module",
        "cover",
        "status",
        "order",
        "has_homework"
    ]

    list_per_page = 50

    list_display_links = [
        'title',
        'cover'
    ]

    list_filter = [
        "status",
        "has_homework",
        "module",
    ]

    list_editable = [
        'status',
        'order'
    ]

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
    list_display = [
        "get_title",
        "get_name",
        "created_at",
        "is_verified",
        "is_done"
    ]

    inlines = [
        CommentNotificationInline
    ]

    readonly_fields = [
        'user',
        'title'
    ]

    list_filter = [
        'is_verified',
        'is_done',
        'created_at',
        'title',
    ]

    list_per_page = 50

    search_fields = [
        'title',
        'user__profile__name'
    ]

    def get_name(self, obj: Notification) -> str:
        name = Profile.objects.get(user=obj.user)
        return name.name

    get_name.short_description = 'Студент'

    def get_title(self, obj: Notification):
        return obj.title

    get_title.short_description = 'Название урока'

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)

        # скрываем user при редактировании
        if obj and 'user' and 'lesson' in fields:
            fields.remove('user')
            fields.remove('lesson')

        return fields


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'get_name',
        'payment_id',
        'payment_status',
        'payment_date',
        'get_amount',
    ]

    list_filter = [
        'payment_status',
        'payment_date',
    ]

    list_per_page = 50

    search_fields = [
        'get_name',
        'payment_id'
    ]

    list_display_links = None

    def get_amount(self, obj):
        return f'{obj.amount:,.0f}'.replace(",", " ") + f' {obj.currency}'

    get_amount.short_description = 'Цена'

    def get_name(self, obj):
        return obj.user.profile.name

    get_name.short_description = 'Студент'
