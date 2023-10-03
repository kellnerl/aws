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
    path("", views.home_discussions, name="home_discussions"),
    path("navigate_back", views.navigate_back, name="navigate_back"),
    path("discussions/<int:section_num>/<str:section_type>", views.discussions, name="discussions"),
    path("discussion_favorite_add/<int:diskuse_id>", views.discussion_favorite_add, name="discussion_favorite_add"),
    path("discussion_favorite_remove/<int:diskuse_id>", views.discussion_favorite_remove, name="discussion_favorite_remove"),
    path("new_discussion/<path:url>/<path:title>/<str:theme>/<str:author>", views.new_discussion, name="new_discussion"),
    path("create_discussion/<path:url>/<path:title>/<str:theme>/<str:author>", views.create_discussion, name="create_discussion"),
    path("home_discussions/", views.home_discussions, name="home_discussions"),
    path("todays_discussions/", views.todays_discussions, name="todays_discussions"),
    path("advanced_search", views.advanced_search, name="advanced_search"),

    path("options_comment/<int:diskuse_id>/<int:comment_id>", views.options_comment, name="options_comment"),
    path("options_comment_thread/<int:diskuse_id>/<int:comment_id>/<int:thread_id>", views.options_comment_thread, name="options_comment_thread"),
    path("reply_comment/<str:operation>/<int:diskuse_id>/<int:comment_id>", views.reply_comment, name="reply_comment"),
    path("reply_comment_thread/<str:operation>/<int:diskuse_id>/<int:comment_id>/<int:thread_id>", views.reply_comment_thread, name="reply_comment_thread"),
    path("new_comment/<int:diskuse_id>", views.new_comment, name="new_comment"),
    path("comment/<int:comment_id>", views.comment, name="comment"),
    path("comment_copy_link/<int:comment_id>", views.comment_copy_link, name="comment_copy_link"),
    path("comments/<int:diskuse_id>", views.comments, name="comments"),
    path("comments_thread/<int:diskuse_id>/<int:thread_id>", views.comments_thread, name="comments_thread"),
    path("user_comments/<int:diskuse_id>/<str:username>", views.user_comments, name="user_comments"),
    path('comment_rate_positive/<int:node_id>', views.comment_rate_positive, name='comment_rate_positive'),
    path('comment_rate_negative/<int:node_id>', views.comment_rate_negative, name='comment_rate_negative'),
    path("about/", views.about, name='about'),
    path("day_events/", views.day_events, name='day_events'),
    path("using_manual/", views.manual, name='using_manual'),
    path("discussion_rules/", views.rules, name='discussion_rules'),

]
