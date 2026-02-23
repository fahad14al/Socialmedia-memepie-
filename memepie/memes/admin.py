from django.contrib import admin
from .models import Meme, Comment, Notification

@admin.register(Meme)
class MemeAdmin(admin.ModelAdmin):
    list_display = ('author', 'caption', 'created_at', 'total_faa_likes')
    search_fields = ('caption', 'author__username')
    list_filter = ('created_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'meme', 'created_at')
    search_fields = ('content', 'author__username')
    list_filter = ('created_at',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'sender', 'notification_type', 'created_at', 'is_read')
    list_filter = ('notification_type', 'is_read', 'created_at')
