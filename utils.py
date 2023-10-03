from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlparse, urlunparse
from django.core.paginator import Paginator

from users.models import UserContext, UserSection

############################
# funkcionalita do první verze:
############################
# nahlásit nevhodný příspěvek
# !!! doladit reset hesla
# dropdown menu u komentáře - (nahlásit, sdílet)
# nginx - konfugurace static, atd, https, ssl certifikáty, počet dotazu jednoho uživatele
# hashování ID (diskuse, komentář, user id)
############################
# funkcionalita k dodělání:
############################
# reCapcha do registrace uživatele
# notifikace
# smajlíky :-) :-(
# přidat jiného uživatele do oblíbených
# https://django-mptt.readthedocs.io/en/latest/templates.html
# komentáře: ? na druhé kliknutí na "reagovat" zavřít editaci pokud k ní ještě nedošlo
# změna emailu -> nová přeaktivace účtu
# sdílet příspěvek na sociálních sítích



def remove_utm_parameters(url):
    finded = url.find('?utm_')
    if finded>0:
        url = url[:finded]
    finded = url.find('&utm_')
    if finded>0:
        url = url[:finded]
    return url

def remove_https_prefix(url):
    if url.startswith('https://'):
        url = url[8:]  # Odstraní prvních 8 znaků (https://)
    return url

def get_page_obj(request, data_set, number_per_page):
    paginator = Paginator(data_set, number_per_page)
    # Get the current page number from the request's GET parameters
    page_number = request.GET.get('page')
    # Get the Page object for the requested page number
    page_obj = paginator.get_page(page_number)
    total_pages = paginator.num_pages 
    return page_obj, total_pages

def check_url_exists(request, url):
    try:
        response = request.head(url)
        return response.status_code == request.codes.ok
    except request.exceptions.RequestException:
        return False

#def get_section_type (request, section):
#    section = UserSection.objects.filter(user=request.user, number=section)[0]
#    return section.type

def get_user_context_instance(request):
    if request.user.is_anonymous:
        if UserContext.objects.filter(ip_address=request.META.get("REMOTE_ADDR", None)).exists():
            user_context_instance = UserContext.objects.get(
                ip_address=request.META.get("REMOTE_ADDR", None))
        else:
            user_context_instance = UserContext()
            user_context_instance.rows_per_page = 10
            user_context_instance.save()
    else:
        if UserContext.objects.filter(user=request.user).exists():
            user_context_instance = UserContext.objects.get(user=request.user)
        else:
            user_context_instance = UserContext()
            user_context_instance.save()
    return user_context_instance

def theme_to_articleTheme (theme):
    theme = theme.lower()
    if theme=="none":
        ret_theme=""
    if theme in ['auto','technika','mobil','věda','mobil']:
        ret_theme="věda technika"
    elif (theme in ['bydlení','brno','ostrava','ústí','hradec','karlovy vary','liberec','praha', 'plzeň', 'olomouc', 'zlín', 'pardubice']):
        ret_theme="společnost"
    elif (theme in ['ekonomika','finance']):
        ret_theme="ekonomika finance"
    elif (theme in ['revue','bulvár']):
        ret_theme="bulvár"
    elif (theme in ['cestování','onadnes','hobby','jenprozeny','bydlení']):
        ret_theme="hobby"
    elif (theme in ['vztahy','sex','xman']):
        ret_theme="vztahy sex"
    elif (theme in ['hry','kultura','hudba','film','koncert','divadlo']):
        ret_theme="kultura"
    elif (theme in ['hokej','fotbal','basketbal', 'atletika','cyklistika','sport']):
        ret_theme="sport"
    else:
        ret_theme=theme.lower()
    return ret_theme

def save_user_context_instance(request, theme_filter, discussion_sort_by, comment_sort_by):
    if request.user.is_anonymous:
        if UserContext.objects.filter(ip_address=request.META.get("REMOTE_ADDR", None)).exists():
            user_context_instance = UserContext.objects.get(
                ip_address=request.META.get("REMOTE_ADDR", None))
            if theme_filter !=  None:
                user_context_instance.default_theme = theme_filter
            if discussion_sort_by:
                user_context_instance.default_discussions_ordering = discussion_sort_by
            if comment_sort_by:
                user_context_instance.default_comments_ordering = comment_sort_by
            user_context_instance.save()
        else:
            user_context_instance = UserContext()
            user_context_instance.ip_address = request.META.get(
                "REMOTE_ADDR", None)
            if theme_filter !=  None:
                user_context_instance.default_theme = theme_filter
            if discussion_sort_by:
                user_context_instance.default_discussions_ordering = discussion_sort_by
            if comment_sort_by:
                user_context_instance.default_comments_ordering = comment_sort_by
            user_context_instance.rows_per_page = 10
            user_context_instance.save()
    else:
        if UserContext.objects.filter(user=request.user).exists():
            user_context_instance = UserContext.objects.get(user=request.user)
            if theme_filter !=  None:
                user_context_instance.default_theme = theme_filter
            if discussion_sort_by:
                user_context_instance.default_discussions_ordering = discussion_sort_by
            if comment_sort_by:
                user_context_instance.default_comments_ordering = comment_sort_by
            user_context_instance.save()
        else:
            print (f"user context pro {request.user} neexistuje !")
 


def get_previous_next_dates(day, month):
    current_date = datetime(year=2023, month=month, day=day)  # Nahraďte za skutečné datum
    previous_date = current_date - timedelta(days=1)
    next_date = current_date + timedelta(days=1)
    
    previous_day = previous_date.day
    previous_month = previous_date.month
    next_day = next_date.day
    next_month = next_date.month
    
    return (previous_day, previous_month), (next_day, next_month)

def time_difference_info(past_time):
    current_time = datetime.now()
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

    if time_info['months'] > 0:
        return (f"{time_info['months']} měsíců")
    elif time_info['days'] > 0:
        return (f"{time_info['days']} dní")
    elif time_info['hours'] > 0:
        return (f"{time_info['hours']} hodin")
    elif time_info['minutes'] > 0:
        return (f"{time_info['minutes']} minut")
    
def save_page(request):
    print (f"request.path {request.path}")
    previous_pages = request.session.get('previous_pages', [])
    if previous_pages:
        if request.path != previous_pages[len(previous_pages)-1]:
            previous_pages.append(request.path)
    else:
        previous_pages.append(request.path)
    request.session['previous_pages'] = previous_pages