from django.db.models.signals import post_save
from django.dispatch import receiver

from discussions.models import Domain, Section
from .models import UserContext, UserDetail, UserSection, UserSectionDomain
from django.contrib.auth.models import User


@receiver(post_save, sender=User)
def create_userContext(sender, instance, created, **kwargs):
    if created:
        # Vytvoření záznamu v UserContext
        UserDetail.objects.create(user=instance, first_name=instance.first_name, last_name=instance.last_name)
        UserContext.objects.create(user=instance)
        sections = Section.objects.filter(active=True)
        for section in sections:
            usersection = UserSection.objects.create(user=instance, name=section.name, type=section.type, description=section.description, number=section.number)

         
@receiver(post_save, sender=UserSection)
def create_userSectionDomain(sender, instance, created, **kwargs):
    if created:
        # Vytvoření záznamů v UserSectionDomain
        usersection = instance
        if usersection.type == 'P':
            section_obj=Section.objects.filter(name=usersection.name)[0]
            domains = Domain.objects.filter(section=section_obj)     
            title = '  '
            print (domains)
            for domain in domains:
                UserSectionDomain.objects.create(userSection=usersection, domain=domain.domain, section_number=usersection.number)
                title = title + domain.domain + ', '
            usersection.title = title[:-2]
            usersection.save()
        elif usersection.type == 'D':
            user_domains = UserSectionDomain.objects.filter(userSection=usersection)     
            title = ' domény:  '
            print (user_domains)
            for domain in user_domains:
                title = title + domain.domain + ', '
            usersection.title = title[:-2]
            usersection.save()
        
@receiver(post_save, sender=UserSectionDomain)
def update_userSection(sender, instance, created, **kwargs):
    if created:
        # Vytvoření záznamů v UserSectionDomain
        usersectiondomain = instance
        usersection = usersectiondomain.userSection
        
        if usersection.type == 'D':
            usersection.title = usersection.title + usersectiondomain.domain + ', '
            usersection.save()
        
        
