from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout as django_logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import UserRegisterForm, UserLoginForm, UserUpdateForm, ProfileUpdateForm
from .models import Block
from django.http import JsonResponse
from django.contrib import messages

@login_required
def profile_edit(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f"Your profile has been updated!")
            return redirect('user_profile', username=request.user.username)
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'accounts/edit_profile.html', context)

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    django_logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('home')

@login_required
def profile_view(request):
    return redirect('user_profile', username=request.user.username)

def signup_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # Update the automatically created profile with extra data
            profile = user.profile
            profile.bio = form.cleaned_data.get('bio')
            if form.cleaned_data.get('profile_pic'):
                profile.profile_pic = form.cleaned_data.get('profile_pic')
            profile.website = form.cleaned_data.get('website')
            profile.birth_date = form.cleaned_data.get('birth_date')
            profile.gender = form.cleaned_data.get('gender')
            profile.save()
            
            username = form.cleaned_data.get('username')
            messages.success(request, f"Welcome {username}! Your account has been created.")
            login(request, user)
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/signup.html', {'form': form})


# ─── Settings Hub ────────────────────────────────────────────────────────────

@login_required
def settings_view(request):
    return render(request, 'accounts/settings.html')


# ─── Change Password ─────────────────────────────────────────────────────────

@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password', '').strip()
        new_password1 = request.POST.get('new_password1', '').strip()
        new_password2 = request.POST.get('new_password2', '').strip()

        if not request.user.check_password(old_password):
            messages.error(request, "Your current password is incorrect.")
        elif new_password1 != new_password2:
            messages.error(request, "New passwords do not match.")
        elif len(new_password1) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
        else:
            request.user.set_password(new_password1)
            request.user.save()
            update_session_auth_hash(request, request.user)  # keep user logged in
            messages.success(request, "Password changed successfully!")
            return redirect('settings')
    return render(request, 'accounts/change_password.html')


# ─── Blocked Accounts ────────────────────────────────────────────────────────

@login_required
def blocked_accounts(request):
    blocks = Block.objects.filter(blocker=request.user).select_related('blocked__profile')
    return render(request, 'accounts/blocked_accounts.html', {'blocks': blocks})

@login_required
def block_user(request, username):
    target = get_object_or_404(User, username=username)
    if target != request.user:
        Block.objects.get_or_create(blocker=request.user, blocked=target)
        messages.success(request, f"@{username} has been blocked.")
    return redirect('user_profile', username=username)

@login_required
def unblock_user(request, username):
    target = get_object_or_404(User, username=username)
    Block.objects.filter(blocker=request.user, blocked=target).delete()
    messages.success(request, f"@{username} has been unblocked.")
    return redirect('blocked_accounts')


# ─── Terms & Policy ──────────────────────────────────────────────────────────

def terms_policy(request):
    return render(request, 'accounts/terms_policy.html')


@login_required
def profile_edit(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f"Your profile has been updated!")
            return redirect('user_profile', username=request.user.username)
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'accounts/edit_profile.html', context)

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    django_logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('home')

@login_required
def profile_view(request):
    return redirect('user_profile', username=request.user.username)

def signup_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # Update the automatically created profile with extra data
            profile = user.profile
            profile.bio = form.cleaned_data.get('bio')
            if form.cleaned_data.get('profile_pic'):
                profile.profile_pic = form.cleaned_data.get('profile_pic')
            profile.website = form.cleaned_data.get('website')
            profile.birth_date = form.cleaned_data.get('birth_date')
            profile.gender = form.cleaned_data.get('gender')
            profile.save()
            
            username = form.cleaned_data.get('username')
            messages.success(request, f"Welcome {username}! Your account has been created.")
            login(request, user)
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/signup.html', {'form': form})
