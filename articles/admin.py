from django.contrib import admin

from articles.models import Article, ArticleUserQuery 

# Register your models here.


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display=['domain', 'title', 'url', 'author', 'theme', 'published_on']

@admin.register(ArticleUserQuery)
class ArticleUserQueryAdmin(admin.ModelAdmin):
    list_display=['key_word', 'section', 'theme', 'days_old', 'published_after', 'published_before']