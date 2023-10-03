from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Max
from .models import Comment, Discussion
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
