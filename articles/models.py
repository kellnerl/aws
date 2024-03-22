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


    

