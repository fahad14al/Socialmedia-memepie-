from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Meme, Comment, Notification, Follow
from accounts.models import Block
from .forms import MemeForm, CommentForm
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q

def get_smart_suggestions(user, limit=None):
    if not user.is_authenticated:
        return []
    
    # 1. Who I already follow
    already_following = Follow.objects.filter(follower=user).values_list('following_id', flat=True)
    
    # 2. Mutual Follows (Followings of followings)
    mutual_follows = User.objects.filter(
        followers__follower_id__in=already_following
    ).exclude(
        Q(id=user.id) | Q(id__in=already_following)
    ).annotate(
        score=Count('id')
    )
    
    # 3. People who liked the same memes (Shared interests)
    liked_meme_ids = user.liked_memes.values_list('id', flat=True)
    shared_interests = User.objects.filter(
        liked_memes__id__in=liked_meme_ids
    ).exclude(
        Q(id=user.id) | Q(id__in=already_following)
    ).annotate(
        score=Count('id')
    )
    
    # Combine and prioritize
    # This is a simple combination. In a real app we'd weight them.
    # We'll use a dictionary to merge scores if we wanted, but here let's just combine queries.
    combined_ids = list(mutual_follows.values_list('id', flat=True)) + list(shared_interests.values_list('id', flat=True))
    
    # If not enough smart suggestions, add random ones
    suggestions = User.objects.filter(id__in=combined_ids).distinct()
    
    count = suggestions.count()
    if limit and count < limit:
        random_ones = User.objects.exclude(
            Q(id=user.id) | Q(id__in=already_following) | Q(id__in=combined_ids)
        ).order_by('?')[:(limit - count)]
        suggestions = list(suggestions) + list(random_ones)
    elif limit:
        suggestions = suggestions[:limit]
        
    return suggestions

def get_personalized_feed(user):
    if not user.is_authenticated:
        return Meme.objects.all().annotate(like_count=Count('faa_likes')).order_by('-like_count', '-created_at')

    # 1. Following
    following_ids = Follow.objects.filter(follower=user).values_list('following_id', flat=True)
    following_memes = Meme.objects.filter(author_id__in=following_ids).order_by('-created_at')
    
    # 2. Interest (Interacted authors)
    # Authors of memes I liked
    liked_author_ids = user.liked_memes.values_list('author_id', flat=True)
    # Authors of memes I commented on
    commented_author_ids = Comment.objects.filter(author=user).values_list('meme__author_id', flat=True)
    
    interacted_author_ids = set(list(liked_author_ids) + list(commented_author_ids))
    interacted_author_ids.discard(user.id) # Remove self
    for fid in following_ids: interacted_author_ids.discard(fid) # Remove already following
    
    interest_memes = Meme.objects.filter(author_id__in=interacted_author_ids).order_by('-created_at')
    
    # 3. Fallback (Popular & Latest)
    # Exclude what we already have
    seen_ids = set(list(following_memes.values_list('id', flat=True)) + list(interest_memes.values_list('id', flat=True)))
    
    fallback_memes = Meme.objects.exclude(id__in=seen_ids).annotate(
        like_count=Count('faa_likes')
    ).order_by('-like_count', '-created_at')
    
    # Combine results maintaining priority
    # Converting to list to maintain order across different querysets
    feed = list(following_memes) + list(interest_memes) + list(fallback_memes)
    return feed

def home(request):
    comment_form = CommentForm()
    
    already_following = []
    suggested_users = []
    memes = []
    
    if request.user.is_authenticated:
        already_following = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
        suggested_users = get_smart_suggestions(request.user, limit=5)
        memes = get_personalized_feed(request.user)
    else:
        memes = Meme.objects.all().annotate(like_count=Count('faa_likes')).order_by('-like_count', '-created_at')
        
    return render(request, 'memes/home.html', {
        'memes': memes, 
        'comment_form': comment_form,
        'suggested_users': suggested_users,
        'already_following': already_following
    })

@login_required
def suggestions_all(request):
    suggested_users = get_smart_suggestions(request.user)
    already_following = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
    return render(request, 'memes/suggestions_all.html', {
        'suggested_users': suggested_users,
        'already_following': already_following
    })

@login_required
def upload_meme(request):
    if request.method == 'POST':
        form = MemeForm(request.POST, request.FILES)
        if form.is_valid():
            meme = form.save(commit=False)
            meme.author = request.user
            meme.save()
            messages.success(request, 'Meme uploaded successfully!')
            return redirect('home')
    else:
        form = MemeForm()
    return render(request, 'memes/upload.html', {'form': form})

from django.http import JsonResponse

@login_required
def like_meme(request, meme_id):
    meme = get_object_or_404(Meme, id=meme_id)
    liked = False
    if request.user in meme.faa_likes.all():
        meme.faa_likes.remove(request.user)
    else:
        meme.faa_likes.add(request.user)
        liked = True
        # Create notification
        if meme.author != request.user:
            Notification.objects.create(
                recipient=meme.author,
                sender=request.user,
                meme=meme,
                notification_type='like',
                text_preview=f"{request.user.username} liked your meme"
            )
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'total_likes': meme.total_faa_likes
        })
    return redirect('home')

@login_required
def add_comment(request, meme_id):
    meme = get_object_or_404(Meme, id=meme_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.meme = meme
            comment.author = request.user
            
            # Handle reply
            parent_id = request.POST.get('parent_id')
            if parent_id:
                parent_comment = get_object_or_404(Comment, id=parent_id)
                comment.parent = parent_comment
            
            comment.save()
            
            # Create notification
            if meme.author != request.user:
                Notification.objects.create(
                    recipient=meme.author,
                    sender=request.user,
                    meme=meme,
                    notification_type='comment',
                    text_preview=f"{request.user.username} commented: {comment.content[:30]}..."
                )
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'comment_id': comment.id,
                    'username': comment.author.username,
                    'profile_pic_url': comment.author.profile.profile_pic.url,
                    'content': comment.content,
                    'created_at': 'Just now',
                    'total_comments': meme.comments.count(),
                    'is_reply': bool(comment.parent),
                    'parent_id': comment.parent.id if comment.parent else None
                })
    return redirect('home')

@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    liked = False
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)
        liked = True
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'total_likes': comment.total_likes
        })
    return redirect('home')

@login_required
def notifications(request):
    notifs = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    # Mark as read
    notifs.filter(is_read=False).update(is_read=True)
    return render(request, 'memes/notifications.html', {'notifications': notifs})

def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    memes = profile_user.memes.all().order_by('-created_at')
    
    followers_count = profile_user.followers.count()
    following_count = profile_user.following.count()
    is_following = False
    is_blocked = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()
        is_blocked = Block.objects.filter(blocker=request.user, blocked=profile_user).exists()
        
    return render(request, 'memes/user_profile.html', {
        'profile_user': profile_user, 
        'memes': memes,
        'followers_count': followers_count,
        'following_count': following_count,
        'is_following': is_following,
        'is_blocked': is_blocked
    })

@login_required
def toggle_follow(request, username):
    to_follow = get_object_or_404(User, username=username)
    if to_follow == request.user:
        return JsonResponse({'status': 'error', 'message': 'You cannot follow yourself'})
    
    follow_obj = Follow.objects.filter(follower=request.user, following=to_follow)
    if follow_obj.exists():
        follow_obj.delete()
        action = 'unfollowed'
    else:
        Follow.objects.create(follower=request.user, following=to_follow)
        action = 'followed'
        # Notification
        Notification.objects.create(
            recipient=to_follow,
            sender=request.user,
            notification_type='follow',
            text_preview=f"{request.user.username} started following you"
        )
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'action': action,
            'followers_count': to_follow.followers.count(),
            'following_count': to_follow.following.count()
        })
    return redirect('user_profile', username=username)

def search(request):
    query = request.GET.get('q', '')
    users = []
    memes = []
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query)
        ).distinct()
        memes = Meme.objects.filter(caption__icontains=query).order_by('-created_at')
    
    return render(request, 'memes/search_results.html', {
        'users': users,
        'memes': memes,
        'query': query
    })

def get_followers(request, username):
    user = get_object_or_404(User, username=username)
    followers = user.followers.all()
    user_list = []
    for f in followers:
        user_list.append({
            'id': f.follower.id,
            'username': f.follower.username,
            'profile_pic_url': f.follower.profile.profile_pic.url
        })
    return JsonResponse({'users': user_list})

def get_following(request, username):
    user = get_object_or_404(User, username=username)
    following = user.following.all()
    user_list = []
    for f in following:
        user_list.append({
            'id': f.following.id,
            'username': f.following.username,
            'profile_pic_url': f.following.profile.profile_pic.url
        })
    return JsonResponse({'users': user_list})
