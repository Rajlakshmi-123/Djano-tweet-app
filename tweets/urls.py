from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='tweets/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('tweet/<int:pk>/', views.tweet_detail_view, name='tweet_detail'),
    path('tweet/<int:pk>/like/', views.like_tweet, name='like_tweet'),
    path('tweet/<int:pk>/delete/', views.delete_tweet, name='delete_tweet'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('profile/<str:username>/follow/', views.follow_toggle, name='follow_toggle'),
    path('profile/edit/me/', views.edit_profile_view, name='edit_profile'),
    path('explore/', views.explore_view, name='explore'),
]