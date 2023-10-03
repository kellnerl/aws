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

urlpatterns = [
    path('user_info/<str:username>', views.user_info, name='user_info'),
    path('user_detail/<int:userid>', views.user_detail, name='user_detail'),
    path('user_context/<int:userid>', views.user_context, name='user_context'),
    path('user_section_operation/<int:userid>/<int:section>/<int:operation>', views.user_section_operation, name='user_section_operation'),
    path('user_section_edit/<int:userid>/<int:section>', views.user_section_edit, name='user_section_edit'),
    path('user_section_new/<int:userid>/<int:number>', views.user_section_new, name='user_section_new'),
    path('user_section_update/<int:userid>/<int:usersectionid>', views.user_section_new, name='user_section_update'),
    path('user_section_domains/<int:usersectionid>', views.user_section_domains, name='user_section_domains'),
    path('user_section', views.UserSectionList.as_view(), name='usersection-list'),
    path('user_section/add/', views.UserSectionDomainCreate.as_view(), name='usersection-add'),
    path('user_section/<int:pk>', views.UserSectionDomainUpdate.as_view(), name='usersection-update'),
    path('user_section/<int:pk>', views.UserSectionDelete.as_view(), name='usersection-delete'),

]
