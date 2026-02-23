from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Thread, Message
from django.contrib.auth.models import User
from memes.models import Meme, Follow
from django.http import JsonResponse

@login_required
def inbox(request):
    show_requests = request.GET.get('tab') == 'requests'
    all_threads = Thread.objects.filter(participants=request.user)
    
    primary_threads = []
    request_threads = []
    
    for thread in all_threads:
        other_user = thread.participants.exclude(id=request.user.id).first()
        thread.other_user = other_user
        
        # Check if it should be in requests
        # Logic: It's NOT a request if:
        # 1. is_accepted is True
        # 2. OR the current user follows the sender (other_user)
        is_following = Follow.objects.filter(follower=request.user, following=other_user).exists()
        
        if thread.is_accepted or is_following:
            primary_threads.append(thread)
        else:
            request_threads.append(thread)
        
        # Add is_unread flag for styling
        thread.is_unread = thread.messages.filter(~Q(sender=request.user), is_read=False).exists()
            
    return render(request, 'direct_messages/inbox.html', {
        'threads': request_threads if show_requests else primary_threads,
        'primary_count': len(primary_threads),
        'request_count': len(request_threads),
        'show_requests': show_requests
    })

@login_required
def chat_detail(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id, participants=request.user)
    messages = thread.messages.all()
    other_user = thread.participants.exclude(id=request.user.id).first()
    
    # Check if this thread is currently a request for the current user
    # (i.e., not accepted and user doesn't follow sender)
    is_following = Follow.objects.filter(follower=request.user, following=other_user).exists()
    is_request = not thread.is_accepted and not is_following
    
    # Pre-calculate thread lists for sidebar
    all_sidebar_threads = Thread.objects.filter(participants=request.user)
    primary_threads = []
    request_threads = []
    for t in all_sidebar_threads:
        t_other = t.participants.exclude(id=request.user.id).first()
        t.other_user = t_other
        t.is_unread = t.messages.filter(~Q(sender=request.user), is_read=False).exists()
        # last message snippet
        last_msg = t.messages.last()
        t.last_message = last_msg
        is_f = Follow.objects.filter(follower=request.user, following=t_other).exists() if t_other else False
        if t.is_accepted or is_f:
            primary_threads.append(t)
        else:
            request_threads.append(t)

    if request.method == 'POST' and not is_request:
        text = request.POST.get('text', '').strip()
        if text:
            Message.objects.create(thread=thread, sender=request.user, text=text)
            thread.save() # Update updated_at
            return redirect('chat_detail', thread_id=thread.id)
            
    # Mark messages as read
    thread.messages.filter(~Q(sender=request.user), is_read=False).update(is_read=True)
    
    return render(request, 'direct_messages/chat.html', {
        'thread': thread,
        'chat_messages': messages,
        'other_user': other_user,
        'primary_threads': primary_threads,
        'request_threads': request_threads,
        'primary_count': len(primary_threads),
        'request_count': len(request_threads),
        'is_request': is_request
    })

@login_required
def accept_message_request(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id, participants=request.user)
    thread.is_accepted = True
    thread.save()
    return redirect('chat_detail', thread_id=thread.id)

@login_required
def decline_message_request(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id, participants=request.user)
    thread.delete()
    return redirect('inbox')

@login_required
def start_chat(request, username):
    other_user = get_object_or_404(User, username=username)
    if other_user == request.user:
        return redirect('inbox')
        
    thread = Thread.objects.filter(participants=request.user).filter(participants=other_user).first()
    
    if not thread:
        thread = Thread.objects.create()
        thread.participants.add(request.user, other_user)
        
        # Auto-accept if there's mutual interest/follow
        # Instagram logic: If I follow them, and they message me, it's accepted? 
        # Actually, if WE follow THEM, we probably want their messages.
        # Let's say: If the other user follows request.user, it should be accepted.
        other_follows_me = Follow.objects.filter(follower=other_user, following=request.user).exists()
        if other_follows_me:
            thread.is_accepted = True
            thread.save()
            
    return redirect('chat_detail', thread_id=thread.id)

@login_required
def share_meme(request, meme_id):
    meme = get_object_or_404(Meme, id=meme_id)
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient_id')
        recipient = get_object_or_404(User, id=recipient_id)
        
        thread = Thread.objects.filter(participants=request.user).filter(participants=recipient).first()
        if not thread:
            thread = Thread.objects.create()
            thread.participants.add(request.user, recipient)
            
        Message.objects.create(thread=thread, sender=request.user, meme=meme)
        thread.save()
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})
