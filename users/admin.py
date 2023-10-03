from django.contrib import admin
from users.models import UserDetail
from users.models import UserContext
from users.models import UserSection
from users.models import UserSectionDomain

# Register your models here.

@admin.register(UserDetail)
class UserDetailAdmin(admin.ModelAdmin):
    list_display=['user', 'about_me', 'sex', 'born_on', 'place_of_residence', 'first_name', 'last_name']


@admin.register(UserContext)
class UserContextAdmin(admin.ModelAdmin):
    list_display=['user', 'default_discussions_ordering', 'default_comments_ordering', 'default_user_comments_ordering']

@admin.register(UserSectionDomain)
class UserSectionDomainAdmin(admin.ModelAdmin):
    list_display=['domain', 'userSection', 'section_number']

@admin.register(UserSection)
class UserSectionAdmin(admin.ModelAdmin):
    list_display=['name', 'user', 'number']



