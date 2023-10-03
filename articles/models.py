from django.db import models

from discussions.models import ArticleTheme
from users.models import UserContext

class Article(models.Model):
    title = models.CharField(max_length=120, null=False)
    description = models.CharField(max_length=400, null=True)
    url = models.URLField(max_length=240, unique=True, null=False)
    domain = models.CharField(max_length=80)
    author = models.CharField(max_length=120, null=True)
    theme = models.CharField(max_length=30)
    published_on = models.DateTimeField()
    discussion = models.BooleanField(default=False, null=False)
    discussion_id = models.IntegerField(default=0, null=False)
    comments_count = models.IntegerField(default=0, null=False)

class ArticleUserQuery(models.Model):
    user = models.ForeignKey(UserContext, null=True, on_delete=models.CASCADE, related_name='user_context_article_query_set')   
    key_word = models.CharField(max_length=120, null=False)
    description = models.CharField(max_length=320, null=True)
    domain = models.CharField(max_length=80)
    section = models.IntegerField(null=True)
    author = models.CharField(max_length=120, null=True)
    theme = models.ForeignKey(ArticleTheme, null=True, blank=True, on_delete=models.SET_NULL, related_name='theme_of_article_query_set')  
    days_old = models.IntegerField(null=True)
    published_before = models.DateTimeField(auto_now=True)
    published_after = models.DateTimeField(auto_now=True)
    

