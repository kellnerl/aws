from django.contrib import admin

from articles.models import Article

# Register your models here.


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display=['domain', 'title', 'url', 'author', 'theme', 'published_on']

