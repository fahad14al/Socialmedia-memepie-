from django.urls import path
from . import views

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('<int:thread_id>/', views.chat_detail, name='chat_detail'),
    path('start/<str:username>/', views.start_chat, name='start_chat'),
    path('share/<int:meme_id>/', views.share_meme, name='share_meme'),
    path('accept/<int:thread_id>/', views.accept_message_request, name='accept_request'),
    path('decline/<int:thread_id>/', views.decline_message_request, name='decline_request'),
]
