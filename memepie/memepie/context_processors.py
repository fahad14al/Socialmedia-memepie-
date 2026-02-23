def unread_counts(request):
    if not request.user.is_authenticated:
        return {}
    
    from direct_messages.models import Message
    from memes.models import Notification
    
    unread_messages_count = Message.objects.filter(
        thread__participants=request.user,
        is_read=False
    ).exclude(sender=request.user).distinct().count()
    
    unread_notifications_count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).distinct().count()
    
    return {
        'unread_messages_count': unread_messages_count,
        'unread_notifications_count': unread_notifications_count
    }
