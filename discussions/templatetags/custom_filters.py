from django import template
from django.utils import timezone
from django.template.defaultfilters import urlize
import requests
import utils
import re
import pytz
from datetime import datetime, timedelta

register = template.Library()

@register.filter(name='comment_cnt_str')
def comment_cnt_str(comments_count):
    if comments_count == 1:
        return f"{comments_count} komentář"
    elif comments_count > 1 and comments_count < 5:
        return f"{comments_count} komentáře"
    elif comments_count > 4:
        return f"{comments_count} komentářů"
    
@register.filter(name='reply_cnt_str')
def reply_cnt_str(replies_count):
    if replies_count == 0:
        return f", žádná reakce"
    elif replies_count < 5:
        return f", {replies_count} reakce"
    elif replies_count > 4:
        return f", {replies_count} reakcí"

@register.filter(name='timediff')
def timediff(past_time):
    #past_time = timezone.make_aware(past_time, timezone.get_current_timezone())

    current_time_utc = timezone.now()

#module 'django.utils.timezone' has no attribute 'pytz'

# Convert the current time to a specific timezone (e.g., 'Europe/Prague')
    desired_timezone = pytz.timezone('Europe/Prague')
    current_time = current_time_utc.astimezone(desired_timezone)

    #current_time = datetime.now()
    time_difference = current_time - past_time

    minutes = time_difference.total_seconds() // 60
    hours = time_difference.total_seconds() // 3600
    days = time_difference.days
    months = (current_time.year - past_time.year) * 12 + current_time.month - past_time.month

    time_info = {
        "minutes": minutes,
        "hours": hours,
        "days": days,
        "months": months
    }

    if time_info['months'] > 1:
        return (f"před {int(time_info['months'])} měsíci")
    elif time_info['months'] == 1:
        return (f"před {int(time_info['months'])} měsícem")
    elif time_info['days'] > 1:
        return (f"před {int(time_info['days'])} dny")
    elif time_info['days'] == 1:
        return (f"před {int(time_info['days'])} dnem")
    elif time_info['hours'] > 1:
        return (f"před {int(time_info['hours'])} hodinami")
    elif time_info['hours'] == 1:
        return (f"před {int(time_info['hours'])} hodinou")
    elif time_info['minutes'] == 1:
        return (f"před {int(time_info['minutes'])} minutou")
    elif time_info['minutes'] > 1:
        return (f"před {int(time_info['minutes'])} minutami")
    elif time_info['minutes'] == 0:
        return (f"právě teď")
    
@register.filter
def linkify(text):
    from django.utils.html import escape
    from django.utils.safestring import mark_safe

    url_pattern = r'(http|https|ftp)\://([a-zA-Z0-9\.\-]+(\:[a-zA-Z0-9\.&%\$\-]+)*@)?((25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9])\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[0-9])|([a-zA-Z0-9\-]+\.)*[a-zA-Z0-9\-]+\.[a-zA-Z]{2,4})(\:[0-9]+)?(/[^/][a-zA-Z0-9\.\,\?\'\\/\+&%\$#\=~_\-@]*)*'
 
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


    result = re.sub(url_pattern, replace, text, flags=re.IGNORECASE)

    return result
    
