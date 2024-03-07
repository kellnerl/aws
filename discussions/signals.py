from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Max
from .models import Comment, Discussion, Domain, Section
from django.contrib.auth.models import User
        

@receiver(post_save, sender=Discussion )
def aktualizovat_discussion_model(sender, instance, created, **kwargs):
    if created:
        user = User.objects.get(username=instance.created_by)
        instance.favorite.add(user.id)
        instance.save()

@receiver(post_save, sender=Comment)
def aktualizovat_discussion_model(sender, instance, created, **kwargs):
    if created:
        discussion = instance.discussion
        parent = instance.parent
        if parent != None:
            replies_count = parent.replies_count
            parent.replies_count = replies_count + 1
            parent.save()
        last_comment = Comment.objects.filter(discussion=discussion.id).aggregate(Max('created_on'))
        discussion.last_comment = last_comment['created_on__max']
        discussion.comments_count = Comment.objects.filter(discussion=discussion.id).count()
        discussion.save()
        

@receiver(post_delete, sender=Comment)
def aktualizovat_discussion_model(sender, instance, **kwargs):      
        discussion = instance.discussion
        parent = instance.parent
        if parent != None:
            replies_count = parent.replies_count
            replies_count = replies_count - 1
            if replies_count < 0:
                 replies_count =0
            parent.replies_count = replies_count
            parent.save()
        #else:
        #    replies_count = instance.replies_count
        #    instance.replies_count = replies_count - 1
        #    instance.save()
        last_comment = Comment.objects.filter(discussion=discussion.id).aggregate(Max('created_on'))
        discussion.last_comment = last_comment['created_on__max']
        discussion.comments_count = Comment.objects.filter(discussion=discussion.id).count()
        discussion.save()

@receiver(post_save, sender=Domain)
def create_Domain(sender, instance, created, **kwargs):
    if created:
        # Title of Section update
        new_domain = instance
        section_obj=Section.objects.get(name=new_domain.section.name)
        domains = Domain.objects.filter(section=section_obj)  
        # Použití seznamové komprehenze a join pro spojení doménových názvů
        #title = ', '.join(domain.domain for domain in domains)    
        title = ''
        for domain in domains:
            title = title + domain.domain + ',\n '
        # Pokud seznam není prázdný, smaž posledni ', ', jinak nastavte na '.'
        title = title[:-3] if len(title) > 1 else '.'
            
        section_obj.title = title
        section_obj.save()

