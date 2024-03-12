"""diskuze URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from django.template.defaultfilters import register

from . import views
from . views import MyPasswordResetView, MyPasswordResetDoneView, MyPasswordResetConfirmView, MyPasswordResetCompleteView



urlpatterns = [
    path('login/', views.LoginInterfaceView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('registration_done/<str:username>', views.registration_done, name='registration_done'),
    path('activate/<str:uidb64>/<str:token>/', views.activate, name='activate'),
    path('activation_failure/', views.activation_failure, name='activation_failure'),
    path('activation_success/', views.activation_success, name='activation_success'),
    path('password_reset/', views.MyPasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', views.MyPasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
  #  path('reset/<uidb64>/<token>/', views.MyPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
  #  path('password_reset_complete/', views.MyPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('reset/', MyPasswordResetView.as_view(), name='password_reset'),
    path('reset/done/', MyPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', MyPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/complete/', MyPasswordResetCompleteView.as_view(), name='password_reset_complete'),

]
