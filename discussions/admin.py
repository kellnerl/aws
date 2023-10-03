from django.contrib import admin

from discussions.models import Section 
from discussions.models import Discussion
from discussions.models import Comment
from discussions.models import Domain
from discussions.models import ArticleTheme
# Register your models here.


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display=['domain', 'section', 'parent']


@admin.register(ArticleTheme)
class ArticleThemeAdmin(admin.ModelAdmin):
    list_display=['name', 'description', 'number']


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display=['number', 'name', 'description', 'active']

@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    list_display=['title', 'description', 'url', 'author', 'theme', 'domain', 'active', 'created_on', 'created_by']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
     list_display=['discussion', 'parent', 'content', 'created_on', 'created_by', 'ip_address']