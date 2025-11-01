from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from Booking.models import MenuItem, User
from django.core.cache import cache
from django.core.mail import send_mail


@receiver([post_save, post_delete], sender=MenuItem)
def invalidate_menuitem_cache(sender, instance, **kwargs):
    '''
    Invalidate menuitem list caches when the menuitem in created, updated, deleted
    this function will be called when post_save or post_delete signal is fired on MenuItem model, when any kind of change occures at MenuItem model using save or delete
    method we want then invalidate all caches objects(keys in the cache) that have prefix menuitem_list we define in view's decorator
    we need to register this signal at apps.py
    '''
    print('Clearing menuitem list cache')
    
    #Clear menuitem list caches
    cache.delete_pattern('*menuitem_list*')     # remove all patterns that containes menuitem_list from the redis database


@receiver(post_save, sender=User, dispatch_uid="send_welcome_email")    #dispatch_uid - unique identifier for a signal receiver in cases when duplicate signals were send
def send_welcome_email(sender, instance, created, **kwargs):
    '''
    Send a welcome email when a new user is created
    '''
    print("Signal fired...")
    if created:
        send_mail(
            'Welcome!', #subject
            'Thanks for signing up!',   #text of email
            'admin@restaurant.com', #from email
            [instance.email], #recipient list
            fail_silently=False,
        )
