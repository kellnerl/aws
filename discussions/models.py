import datetime
from glob import escape
import utils
from django.db import models
from django.db.models import Max
from django.db.models.deletion import CASCADE
from django.db.models.signals import post_save
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.db.models import Q
from django.dispatch import receiver
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import User
import requests
from diskuze import settings
from urllib.parse import urlparse
import tldextract
import re

# Create your models here.

sprosta_slova = ['piča', 'pičo', 'píča', 'píčo', 'hajzl', 'hajzle', 'debile', 'mrdko', 'svině', 'mrdka',
                 'pičus', 'zmrd', 'zmrde', 'zmrda', 'čurák', 'čuráka','čuráku', 'debile', 'kretene', 'hovado']


def cenzurovat_text(text, sprosta_slova):
    cenzurovany_text = text
    for slovo in sprosta_slova:
        cenzurovany_text = re.sub(r'\b' + re.escape(slovo) + r'\b',
                                  '*' * len(slovo), cenzurovany_text, flags=re.IGNORECASE)
    return cenzurovany_text


class Region(models.Model):
    name = models.CharField(max_length=60, unique=True)
    abbrevation = models.CharField(max_length=2, unique=True)  
    lang = models.CharField(max_length=2, unique=False)

#models.ForeignKey(Section, on_delete=models.CASCADE, null=True, blank=True, related_name='section_set')


class Section(models.Model):
    name = models.CharField(max_length=60, unique=True)
    description = models.CharField(max_length=240, null=True)
    number = models.IntegerField(default=0, unique=True)
    region = models.CharField(max_length=2, default='cz', null=False)
    scrapping = models.BooleanField(default=False, null=False)
    active = models.BooleanField(default=True)
    type = models.CharField(max_length=1, null=False, default='P') # 'M'-mine discussion, 'P'-preddefined section, 'U'-user defined section


    @property
    def tabname_s (self):
      return "tab_"+str(self.name)

    def __str__(self):
        return self.name


class Domain(models.Model):
    domain = models.CharField(max_length=60, unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE,
                            null=True, blank=True, related_name='children')
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, null=True, blank=True, related_name='section_set')

    def __str__(self):
        return self.domain


class ArticleTheme(models.Model):
    name = models.CharField(max_length=60, unique=True)
    description = models.CharField(max_length=240, null=True)
    number = models.IntegerField(unique=True)

    def __str__(self):
        return self.name


class Discussion(models.Model):
    title = models.CharField(max_length=120, null=False)
    description = models.CharField(max_length=320, null=True)
    url = models.URLField(max_length=240, unique=True, null=False)
    domain = models.CharField(max_length=80)
    author = models.CharField(max_length=120, null=True)
    theme = models.ForeignKey(ArticleTheme, null=True, blank=True, on_delete=models.SET_NULL, related_name='theme_of_dicsussion_set')
    last_comment = models.DateTimeField(null=True)
    comments_count = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    favorite = models.ManyToManyField(User)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, null=True, on_delete=models.CASCADE, related_name='author_of_discusses_set')

    @property
    def basic_comments_count(self):
        x = 0
        try:
            x = Comment.objects.filter(discussion=self.id, parent=None).count()
        except:
            pass
        return x

    @property
    def replies_count(self):
        x = 0
        try:
            x = Comment.objects.filter(
                discussion=self.id).exclude(parent=None).count()
        except:
            pass
        return x

    def save(self, *args, **kwargs):
        extracted = tldextract.extract(self.url)
        # Get the first-level domain
        first_level_domain = extracted.domain + '.' + extracted.suffix
        domain = extracted.subdomain + '.' + first_level_domain
        self.domain = domain
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Comment(MPTTModel):
    discussion = models.ForeignKey(
        Discussion, null=True, blank=True, on_delete=CASCADE, related_name='comments_set')
    parent = TreeForeignKey('self', on_delete=models.PROTECT,
                            null=True, blank=True, related_name='children')
    content = models.TextField()
    root_id = models.IntegerField(default=0, null=False)
    plus = models.IntegerField(default=0)
    minus = models.IntegerField(default=0)
    replies_count = models.IntegerField(default=0, null=False)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, null=True, related_name="author_of_comments_set", on_delete=models.CASCADE)
    evaluator = models.ManyToManyField(User)
   # wrong_reported = models.ManyToManyField(User)
    ip_address = models.GenericIPAddressField(null=True)

    class Meta:
        ordering = ('-created_on', 'lft')

    class MPTTMeta:
        order_insertion_by = ['-created_on', 'lft']

   



    def save(self, *args, **kwargs):

    # Funkce, která nahradí slovo "url" řetězcem "xxx"
        def replace (value):
            value = utils.remove_utm_parameters(value.group(0))
            try:
                response = requests.head(value)
                if response.status_code == 200:
                    return mark_safe(f'<a href="{escape(value)}">{escape(value)}</a>')
                else:
                    return escape(value)
            except requests.exceptions.RequestException:               
                return escape(value)

        self.content = cenzurovat_text(self.content, sprosta_slova)
        self.content = utils.remove_utm_parameters(self.content)
        print (f"self.id {self.id}")
        if self._state.adding and self.id is None:
            if self.parent == None:
                super().save(*args, **kwargs)
                self.root_id = self.id
                self.save(update_fields=['root_id'])
            else:
                self.root_id = self.parent.root_id

        
        url_pattern = r'(http|https|ftp)\://([a-zA-Z0-9\.\-]+(\:[a-zA-Z0-9\.&%\$\-]+)*@)?((25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9])\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[0-9])|([a-zA-Z0-9\-]+\.)*[a-zA-Z0-9\-]+\.[a-zA-Z]{2,4})(\:[0-9]+)?(/[^/][a-zA-Z0-9\.\,\?\'\\/\+&%\$#\=~_\-@]*)*'
 
        self.content = re.sub(url_pattern, replace, self.content, flags=re.IGNORECASE)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.content
