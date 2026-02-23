from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_meme, name='upload_meme'),
    path('like/<int:meme_id>/', views.like_meme, name='like_meme'),
    path('comment/<int:meme_id>/', views.add_comment, name='add_comment'),
    path('comment/like/<int:comment_id>/', views.like_comment, name='like_comment'),
    path('notifications/', views.notifications, name='notifications'),
    path('suggestions/', views.suggestions_all, name='suggestions_all'),
    path('search/', views.search, name='search'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('profile/<str:username>/follow/', views.toggle_follow, name='toggle_follow'),
    path('profile/<str:username>/followers/', views.get_followers, name='get_followers'),
    path('profile/<str:username>/following/', views.get_following, name='get_following'),
]
