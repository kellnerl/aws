import tldextract
from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class UserDetail(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE, related_name='user_detail_set') 
    favorite = models.ManyToManyField(User)  
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    verified = models.BooleanField(default=False)
    about_me = models.TextField(max_length=480,null=True)
    displayed_username = models.CharField(max_length=100, null=True)
    ip_address = models.GenericIPAddressField(null=True)
    photo = models.ImageField(upload_to='photos/')
    sex = models.CharField(max_length=1, null=True)
    born_on = models.DateField(null=True)
    place_of_residence = models.CharField(max_length=160, null=True)
   

class UserContext(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE, related_name='user_context_set')   
    display_fullname = models.BooleanField(default=False)
    display_time_difference = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True)
    rows_per_page = models.IntegerField(default=10, null=False)
    days_in_new_tabs = models.IntegerField(default=2, null=False)
    auto_show_all_replies = models.BooleanField(default=False)
    notify_on_discussion = models.BooleanField(default=False)
    notify_on_comment = models.BooleanField(default=False)
    notify_on_favorite = models.BooleanField(default=False)
    default_theme = models.IntegerField(default=0)
    default_discussions_ordering = models.IntegerField(default=1)
    default_comments_ordering = models.IntegerField(default=1)
    default_user_comments_ordering = models.IntegerField(default=1)


class UserSection(models.Model):
  user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='user_section_set')   
  name = models.CharField(max_length=60, null=False)
  default = models.BooleanField(default=False)
  title = models.CharField(max_length=160, null=True)
  description = models.CharField(max_length=240, null=True)
  number = models.IntegerField(default=1, null=False)
  type = models.CharField(max_length=1, null=False, default='P') # 'M'-main discussion, 'P'-preddefined section, 'U'-user defined section

  @property
  def tabname (self):
      return "tab"+str(self.number)

  @property
  def tabname_s (self):
      return "tab_"+str(self.name)

  def __str__(self):
      return self.name

class UserSectionDomain(models.Model):
  domain = models.CharField(max_length=60, null=True)
  userSection = models.ForeignKey(UserSection, null=True, on_delete=models.CASCADE, related_name='user_section_set')   
  section_number=models.IntegerField(default=1, null=False)

  #@property
  #def first_level_domain (self):
  #    extracted = tldextract.extract(self.domain)
  #    return extracted.domain + '.' + extracted.suffix
  

  def __str__(self):
      return self.domain
  
