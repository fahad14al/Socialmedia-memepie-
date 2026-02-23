from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('profile/', views.profile_view, name='profile'),
    path('edit/', views.profile_edit, name='profile_edit'),
    path('settings/', views.settings_view, name='settings'),
    path('settings/password/', views.change_password, name='change_password'),
    path('settings/blocked/', views.blocked_accounts, name='blocked_accounts'),
    path('settings/block/<str:username>/', views.block_user, name='block_user'),
    path('settings/unblock/<str:username>/', views.unblock_user, name='unblock_user'),
    path('terms/', views.terms_policy, name='terms_policy'),
]
