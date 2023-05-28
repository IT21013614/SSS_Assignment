from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.register, name='register'),
    path('classify_message/', views.classify_message, name='classify_message'),

    # API Routes
    path('emails', views.compose, name='compose'),
    path('emails/<int:email_id>', views.email, name='email'),
    path('emails/<str:mailbox>', views.mailbox, name='mailbox'),
]