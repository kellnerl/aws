
import re
from datetime import date
from datetime import datetime, timedelta
from django.utils import timezone
from urllib.parse import quote
from urllib.parse import urlencode
import requests
import utils
from django.forms import ValidationError
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import TemplateView
from django.views.generic import CreateView
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse, reverse_lazy
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models import QuerySet
from mptt.templatetags.mptt_tags import cache_tree_children


from discussions.forms import CommentCopyLinkForm, CommentReplyForm, CreateDiscussionForm, AdvancedSearchDiscussionForm, SearchDiscussionForm
from discussions.forms import CommentForm
from discussions.models import Discussion, Comment, Domain, Section
from users.models import UserContext, UserSection, UserSectionDomain
from discussions.models import ArticleTheme


# Create your views here.


def get_sections (request):

    if request.user.is_anonymous:
        queryset = list()
        id=1
        home = UserSection(id=id,name='diskuse', number=id-1, user=None, description='diskuse homepage')
        id=2
        new = UserSection(id=id,name='nové', number=1, user=None, type='T', description='nové diskuse')
        queryset.append(home)  # Přidání home fiktivního prvku do seznamu
        queryset.append(new)  # Přidání new doscussions fiktivního prvku do seznamu
        sections = Section.objects.filter(scrapping=True)
        for section in sections:
           id=id+1
           new_section = UserSection(id=id, name=section.name, number=id, user=None, title=section.title, type=str(section.id), description=section.description)
           queryset.append(new_section) 
        return queryset #sorted(queryset, key=lambda x: x.number)
    else:
        sections = UserSection.objects.filter(user=request.user)
        novy_queryset = list(sections)  # Převedení existujícího QuerySetu na seznam
        home = UserSection(name='diskuse', number=0, user=request.user, title='noncensura home page', description='noncensura home page')  # Vytvoření fiktivního prvku  
        novy_queryset.append(home)  # Přidání fiktivního prvku do seznamu
        return sorted(novy_queryset, key=lambda x: x.number)

def navigate_back(request):
    
    previous_pages = request.session.get('previous_pages', [])
    print (previous_pages)
    if previous_pages:
        previous_pages.pop()  # Odebrat aktuální stránku
        print (previous_pages)
        request.session['previous_pages'] = previous_pages
        if previous_pages:
            print (previous_pages[-1])
            return redirect(previous_pages[-1])
    
    return redirect('home_discussions')  # Pokud není další stránka, přesměrovat na výchozí stránku



def home(request):
    #request.session['previous_url'] = request.META.get('HTTP_REFERER')
    utils.save_page(request)
    section = 0
    return redirect('home_discussions', section)


def about(request):
    #request.session['previous_url'] = request.META.get('HTTP_REFERER')
    utils.save_page(request)
    return render(request, "home/about.html", { })

def rules(request):
    #request.session['previous_url'] = request.META.get('HTTP_REFERER')
    utils.save_page(request)
    return render(request, "home/discussion_rules.html", {})

def manual(request):
    #request.session['previous_url'] = request.META.get('HTTP_REFERER')
    utils.save_page(request)
    return render(request, "home/using_manual.html", { })

def day_events(request):
    #request.session['previous_url'] = request.META.get('HTTP_REFERER')
    daydelta = request.GET.get('daydelta')
    if not daydelta:
        daydelta = 'today'
    utils.save_page(request)
    now = datetime.now()
    month = now.month
    day = now.day
    previous_date, next_date = utils.get_previous_next_dates(day, month)
    if (daydelta == 'tommorow'):
        day=next_date[0]
        month=next_date[1]
    elif (daydelta == 'yesterday'):
        day=previous_date[0]
        month=previous_date[1]

    url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{month}/{day}"
    response = requests.get (url)
    data = response.json()
    events_list =[]
    if "events" in data and len(data["events"]) > 0:
        for event in data["events"]:
            events_list.append({'year': event["year"], 'text': event["text"]})

    return render(request, "home/on_day_events.html", {'events': events_list, 'daydelta': daydelta,'day':day, 'month':month})

@login_required(login_url='/accounts/login')
def comment_rate_positive(request, node_id):
    if request.method == 'POST':
     #  if request.method == 'POST' and request.is_ajax():
        # Zvýšení hodnoty v databázi - zde můžete provést další akce
        # ...
        comment_instance = Comment.objects.get(id=node_id)
        evaluator_instances = comment_instance.evaluator.filter(
            username=request.user)
        if evaluator_instances is None or len(evaluator_instances) == 0:
            comment_instance.plus = comment_instance.plus + 1
            comment_instance.save()
            evaluator_instance = User.objects.get(id=request.user.id)
            comment_instance.evaluator.add(evaluator_instance.id)

        return JsonResponse({'status': 'success', 'message': 'hodnota změněna úspěšně', 'data': {
            'new_value': f"+{comment_instance.plus}",
        }})
    else:
        return JsonResponse({'status': 'error'}, status=400)

@login_required(login_url='/accounts/login')
def discussion_favorite_add(request, diskuse_id):
    Discussion.objects.get(id=diskuse_id).favorite.add(request.user)
    return redirect('comments', diskuse_id=str(diskuse_id))

@login_required(login_url='/accounts/login')
def discussion_favorite_remove(request, diskuse_id):
    Discussion.objects.get(id=diskuse_id).favorite.remove(request.user)
    return redirect('comments', diskuse_id=str(diskuse_id))

@login_required(login_url='/accounts/login')
def comment_rate_negative(request, node_id):
    if request.method == 'POST':
     #  if request.method == 'POST' and request.is_ajax():
        # Zvýšení hodnoty v databázi - zde můžete provést další akce
        # ...
        comment_instance = Comment.objects.get(id=node_id)
        evaluator_instances = comment_instance.evaluator.filter(
            username=request.user)
        if evaluator_instances is None or len(evaluator_instances) == 0:
            comment_instance.minus = comment_instance.minus + 1
            comment_instance.save()
            evaluator_instance = User.objects.get(id=request.user.id)
            comment_instance.evaluator.add(evaluator_instance.id)

        return JsonResponse({'status': 'success', 'message': 'hodnota změněna úspěšně', 'data': {
            'new_value': f"-{comment_instance.minus}",
            # další aktualizovaná data
        }})
    else:
        return JsonResponse({'status': 'error'}, status=400)


def home_discussions(request):
    #request.session['previous_url'] = request.META.get('HTTP_REFERER')
    previous_pages = [request.path]
    request.session['previous_pages'] = previous_pages
    sort_by = request.GET.get('sort_by')
    theme_filter = request.GET.get('theme')
    search_value = request.GET.get('search_value')
    user_context_instance = utils.get_user_context_instance(request)
    if sort_by == None:
        sort_by = user_context_instance.default_discussions_ordering
    else:
        sort_by = int(sort_by)
    if theme_filter == None:
        theme_filter = user_context_instance.default_theme
    else:
        theme_filter = int(theme_filter)
    utils.save_user_context_instance(request, theme_filter, sort_by, None)
    if request.method == 'GET':
        if 'clear' in request.GET:
            return redirect('home_discussions')
        else:
            form = SearchDiscussionForm(request.GET or None)
            if form.is_valid():
                search_value = utils.remove_utm_parameters(form.cleaned_data['search_value'])
                search_pattern = r'\m' + re.escape(search_value) + r'\M'
                diskuses = Discussion.objects.filter(Q(title__iregex=search_pattern) | Q(url__iregex=search_pattern))
                #search_pattern = r'\b' + re.escape(search_value) + r'\b'
                #diskuses = Discussion.objects.filter(Q(title__regex=search_pattern) | Q(url__regex=search_pattern))
                if len(diskuses) == 0:
                    try:
                        response = requests.head(search_value)
                        if response.status_code == 200:
                            return redirect('new_discussion', url=search_value, title="none", theme="none", author="none")
                    except:
                        pass
                if theme_filter > 0:
                    diskuses = diskuses.filter(theme=theme_filter)
                if (sort_by == 1):
                    diskuses = diskuses.order_by('-created_on')
                elif (sort_by == 2):
                    diskuses = diskuses.order_by('-comments_count')
                else:
                    diskuses = diskuses.order_by('-last_comment')
                page_obj, total_pages = utils.get_page_obj(request, diskuses, user_context_instance.rows_per_page)
                sections = get_sections (request)
                form = SearchDiscussionForm(initial={'search_value': search_value})
                context = {
                'form_discussion': form,
                'theme_number': theme_filter,
                'themes': ArticleTheme.objects.all().order_by('number'),
                'section': 0,
                'sections': sections,
                'sort_by': sort_by,
                'page_obj': page_obj,
                'total_pages': total_pages,
                'search_value': search_value,
                }
                return render(request, "discussions/discussions.html", context)
    else:
        form = SearchDiscussionForm(initial={'search_value': search_value})
    user_context_instance = utils.get_user_context_instance(request)
    sections = get_sections (request)
    context = {
        'section': 0,
        'sort_by': sort_by,
        'theme_number': theme_filter,
        'page_obj': [],
        'sections': sections,
        'themes': ArticleTheme.objects.all().order_by('number'),
        'form_discussion': form,
        'search_value': search_value,
        'display_time': user_context_instance.display_time_difference,
    }
    return render(request, "discussions/discussions.html", context)


def advanced_search(request):
    #request.session['previous_url'] = request.META.get('HTTP_REFERER')
    utils.save_page(request)
    if request.method == 'POST':
        form = AdvancedSearchDiscussionForm(request.POST)
        if form.is_valid():
            domain = form.cleaned_data['domain_field']
            title = form.cleaned_data['title']
            theme = form.cleaned_data['theme_field']
            author = form.cleaned_data['author']
            active = form.cleaned_data['active']
            search_value_created_before = form.cleaned_data['search_value_created_before']
            search_value_created_after = form.cleaned_data['search_value_created_after']
            search_value_last_comment_before = form.cleaned_data['search_value_last_comment_before']
            search_value_last_comment_after = form.cleaned_data['search_value_last_comment_after']
            sort_by = int(form.cleaned_data['orderby'])
            print("sort_by")
            print(sort_by)
            # můžete použít metodu filter() spolu s podmínkami pro jednotlivá pole a operátorem __gt (větší než) nebo __gte (větší nebo rovno).
            #records = MyModel.objects.filter(field1__gt=value1, field2__gt=value2, field3__gte=value3)
            diskuses = Discussion.objects.filter(active=active)
            
            if domain:
                diskuses = diskuses.filter(domain=domain)
            if title:
                diskuses = diskuses.filter(Q(title__icontains=title))
            if author:
                diskuses = diskuses.filter(Q(author__icontains=author))
            if theme:
                diskuses = diskuses.filter(theme=theme)
            if search_value_created_before:
                diskuses = diskuses.filter(
                    created_on__lt=search_value_created_before)
            if search_value_created_after:
                diskuses = diskuses.filter(
                    created_on__gt=search_value_created_after)
            if search_value_last_comment_before:
                diskuses = diskuses.filter(
                    last_comment__lt=search_value_last_comment_before)
            if search_value_last_comment_after:
                diskuses = diskuses.filter(
                    last_comment__gt=search_value_last_comment_after)
            if (sort_by == 1):
                diskuses = diskuses.order_by('-created_on')
            elif (sort_by == 2):
                diskuses = diskuses.order_by('-comments_count')
            else:
                diskuses = diskuses.order_by('-last_comment')
            user_context_instance = utils.get_user_context_instance(request)
            page_obj, total_pages = utils.get_page_obj(request, diskuses, user_context_instance.rows_per_page)      
            themes = ArticleTheme.objects.all().order_by('number')
            form = AdvancedSearchDiscussionForm(initial={'title': title, 'author':author, 
                                                         'domain_field': domain, 'theme_field': theme,
                                                         'search_value_created_before':search_value_created_before,
                                                         'search_value_created_after':search_value_created_after,
                                                         'search_value_last_comment_before':search_value_last_comment_before,
                                                         'search_value_last_comment_after':search_value_last_comment_after,
                                                         'orderby': sort_by,
                                                         }
                                                         )
       
            context = {
                'form': form,
                'themes': themes,
                'diskuses': diskuses,
                'section': 0,
                'page_obj': page_obj,
                'total_pages': total_pages,
                'display_time': user_context_instance.display_time_difference,
            }
            return render(request, "discussions/discussions_search.html", context)
        return redirect('advanced_search')
    else:
        sort_by = 1
        form = AdvancedSearchDiscussionForm(initial={'orderby': sort_by,})

    user_context_instance = utils.get_user_context_instance(request)
    context = {
        'form': form,
        'section': 0,
    }
    return render(request, "discussions/discussions_search.html", context)


@login_required(login_url='/accounts/login')
def new_discussion(request, url, title, theme, author):
    #request.session['previous_url'] = request.META.get('HTTP_REFERER')
    utils.save_page(request)
    url_param = url
    if title=="none":
        title_param = ""
    else:
        title_param = title
    if theme=="none":
        theme_param = ""
    else:
        name=utils.theme_to_articleTheme(theme)
        print(f"name {name}")
        theme = ArticleTheme.objects.filter(name=name)
        if theme.count() > 0:
            theme_param = theme[0].id
        else:
            theme_param = 0
    if author=="none":
        author_param = ""
    else:
        author_param = author
    if request.method == 'POST':
        form = CreateDiscussionForm(request.POST)
        if form.is_valid():
            print ("form valid")
            new_discussion = form.save(commit=False)
            selected_theme = form.cleaned_data['theme_field']  # Získání vybrané hodnoty
            if selected_theme:
                new_discussion.theme = ArticleTheme.objects.get(id=selected_theme)
            new_discussion.created_by = request.user
            new_discussion.url = utils.remove_utm_parameters(form.cleaned_data['url'])
            new_discussion.ip_address = request.META.get("REMOTE_ADDR", None)
            new_discussion.save()
            return redirect('comments', diskuse_id=str(new_discussion.id))
        else:
            print ("form not valid")
            url = form.data['url']
            # Kontrola existence URL
            response = requests.head(url)
            if response.status_code != 200:
                print (f"url neexistuje {url}")
                pass
            # Kontrola unikátnosti URL v modelu Article
            if Discussion.objects.filter(url=url).exists():
                diskuse = Discussion.objects.filter(url=url)
                return redirect('comments', diskuse_id=str(diskuse[0].id))
    else:  
        form = CreateDiscussionForm(initial={'url':url_param, 'title':title_param, 'theme_field':theme_param, 'author':author_param})
    return render(request, "discussions/discussion_new.html", {'form': form, 'central': True})


@login_required(login_url='/accounts/login')
def create_discussion(request, url, title, theme, author):
    if author=="none":
        author=""
    articleTheme = None
    articleThemes = ArticleTheme.objects.filter(name=utils.theme_to_articleTheme(theme))
    if articleThemes.count() > 0:
        articleTheme = articleThemes[0]
    new_discussion = Discussion()
    new_discussion.created_by = request.user
    new_discussion.url = utils.remove_utm_parameters(url)
    new_discussion.title = title
    new_discussion.theme = articleTheme
    new_discussion.author = author
    new_discussion.save()
    return redirect('comments', diskuse_id=str(new_discussion.id))

def todays_discussions(request):
    #request.session['previous_url'] = request.META.get('HTTP_REFERER')
    utils.save_page(request)
    theme_filter = request.GET.get('theme')
    sort_by = request.GET.get('sort_by')
    user_context_instance = utils.get_user_context_instance(request)
    if sort_by == None:
        sort_by = user_context_instance.default_discussions_ordering
    else:
        sort_by = int(sort_by)
    if theme_filter == None:
        theme_filter = user_context_instance.default_theme
    else:
        theme_filter = int(theme_filter)
    utils.save_user_context_instance(request, theme_filter, sort_by, None)
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    diskuses = Discussion.objects.filter(created_on__date__in=[today, yesterday])

    if theme_filter > 0:
        diskuses = diskuses.filter(theme=theme_filter+1)
    if (sort_by == 1):
        diskuses = diskuses.order_by('-created_on')
    elif (sort_by == 2):
        diskuses = diskuses.order_by('-comments_count')
    else:
        diskuses = diskuses.order_by('-last_comment')

    user_context_instance = utils.get_user_context_instance(request)
    page_obj, total_pages = utils.get_page_obj(request, diskuses, user_context_instance.rows_per_page)

    sections = get_sections (request)
    context = {
        'section': 0,
        'sort_by': sort_by,
        'theme_number': theme_filter,
        'page_obj': page_obj,
        'total_pages': total_pages,
        'sections': sections,
        'themes': ArticleTheme.objects.all().order_by('number'),
        'form_discussion': SearchDiscussionForm(),
        'today': today,
    }
    return render(request, "discussions/discussions.html", context)

def discussions(request, section_num, section_type):
    #request.session['previous_url'] = request.META.get('HTTP_REFERER')
    utils.save_page(request)
    print (f"section type: {section_type}")
    sort_by = request.GET.get('sort_by')
    theme_filter = request.GET.get('theme')
    user_context_instance = utils.get_user_context_instance(request)
    if sort_by == None:
        sort_by = user_context_instance.default_discussions_ordering
    else:
        sort_by = int(sort_by)
    if theme_filter == None:
        theme_filter = int(user_context_instance.default_theme)
    else:
        theme_filter = int(theme_filter)
    utils.save_user_context_instance(request, theme_filter, sort_by, None)

    if section_type=='M':
        diskuses = Discussion.objects.filter(favorite=request.user)
    elif section_type=='T':
        today = timezone.now().date()
        print (f"today {today}")
        yesterday = today - timedelta(days=1)
        print (f"yesterday {yesterday}")
        diskuses = Discussion.objects.filter(created_on__date__in=[today, yesterday])
    else:
        if request.user.is_anonymous:
            #section = Section.objects.filter(number=section_num, type=section_type)[0]
            section = Section.objects.filter(number=section_num)[0]
            user_domains = Domain.objects.filter(section=section)
        else:
            user_section = UserSection.objects.filter(number=section_num,user=request.user)[0]
            user_domains = UserSectionDomain.objects.filter(userSection=user_section)
        diskuses = Discussion.objects.filter(domain__in=user_domains.values_list('domain', flat=True))
     #   diskuses = Discussion.objects.filter(first_level_domain__in=domains.values_list('first_level_domain', flat=True))
    
    if theme_filter > 0:
        diskuses = diskuses.filter(theme=theme_filter+1)

    if (sort_by == 1):
        diskuses = diskuses.order_by('-created_on')
    elif (sort_by == 2):
        diskuses = diskuses.order_by('-comments_count')
    else:
        diskuses = diskuses.order_by('-last_comment')
    page_obj, total_pages = utils.get_page_obj(request, diskuses, user_context_instance.rows_per_page)
    ###total_pages =0
    ###page_obj=None
    sections = get_sections (request)
    themes = ArticleTheme.objects.all().order_by('number')

    if request.method == 'POST':
        if 'cancel' in request.POST:
            pass
        else:
            form = SearchDiscussionForm(request.POST)
            if form.is_valid():
                try:
                    new_discussion = form.save(commit=False)
                    new_discussion.created_by = request.user
                    new_discussion.url = utils.remove_utm_parameters(form.cleaned_data['url'])     
                    new_discussion.save()
                    diskuse = Discussion.objects.get(url=url)
                    return redirect('comments', diskuse_id=str(diskuse.id))
                except ValidationError as e:
                # Zpracování chyby validace
                    error_code = e.code
                    if error_code == 'invalid_url':
                        pass
                #    form.url.errors ='Neplatná URL'
                    elif error_code == 'article_exists':
                        url = form.data['url']
                        diskuse = Discussion.objects.filter(url=url)
                        return redirect('comments', diskuse_id=str(diskuse.id))
                    else:
                        form = SearchDiscussionForm()
            else:
                url = form.data['url']
                # Kontrola existence URL
                response = requests.head(url)
                if response.status_code != 200:
                    pass
            # Kontrola unikátnosti URL v modelu Article
                if Discussion.objects.filter(url=url).exists():
                    diskuse = Discussion.objects.filter(url=url)
                    return redirect('comments', diskuse_id=str(diskuse.id))

    else:
        form = SearchDiscussionForm()

    context = {
        'section': section_num,
        'sort_by': sort_by,
        'theme_number': theme_filter,
        'page_obj': page_obj,
        'total_pages': total_pages,
        'sections': sections,
        'themes': themes,
        'form_discussion': form,
        'display_time': user_context_instance.display_time_difference,
    }
    return render(request, "discussions/discussions.html", context)

def comment(request, comment_id):
    #request.session['previous_url'] = request.META.get('HTTP_REFERER')
    utils.save_page(request)

    # Získání všech kategorií první úrovně, kde parent = None
    comment = Comment.objects.get(id=comment_id)
    context = {
        'comment': comment,
        'diskuse_id': comment.discussion.id,
        'diskuse_title': comment.discussion.title,
        'diskuse_url': comment.discussion.url,
        'discussion': comment.discussion,   
    }
    return render(request, "comments/comment_detail.html", context)

def comment_copy_link(request, comment_id):
    #request.session['previous_url'] = request.META.get('HTTP_REFERER')
    utils.save_page(request)

    # Získání všech kategorií první úrovně, kde parent = None
    if request.method == 'POST':
        form = CommentCopyLinkForm(request.POST)
        return redirect('navigate_back')
    comment = Comment.objects.get(id=comment_id)
    full_url = request.build_absolute_uri()
    full_url = request.path
    full_url = request.build_absolute_uri().split(request.get_full_path())[0]
    comment_url=f"{full_url}/comment/{comment.id}"
    form = CommentCopyLinkForm(initial={'url': comment_url})
    context = {
        'form': form,
        'comment_id': comment.id,
    }
    return render(request, "comments/comment_copy_link.html", context)
   

def comments(request, diskuse_id):
    #request.session['previous_url'] = request.META.get('HTTP_REFERER')
    utils.save_page(request)

    # Získání všech kategorií první úrovně, kde parent = None
    sort_by = request.GET.get('sort_by')
    user_context_instance = utils.get_user_context_instance(request)
    if sort_by == None:
        sort_by = user_context_instance.default_comments_ordering
    else:
        sort_by = int(sort_by)
    if sort_by > 3:
        sort_by=1
    utils.save_user_context_instance(request, None, None,  sort_by)
    if diskuse_id == 0:
        return redirect('home_discussions')
    else:
        discussion = Discussion.objects.get(id=diskuse_id)

    if sort_by==1:
        root_comments = Comment.objects.filter(discussion = discussion, parent__isnull=True).order_by('-created_on')
    elif sort_by==2:
        root_comments = Comment.objects.filter(discussion = discussion, parent__isnull=True).order_by('-replies_count')
    elif sort_by==3:
        root_comments = Comment.objects.filter(discussion = discussion, parent__isnull=True).order_by('-plus')
    for elem in root_comments:
        reply_comments = Comment.objects.filter(root_id = elem.root_id)
        cache_tree_children(reply_comments)
        elem.reply_comments = reply_comments
    page_obj, total_pages = utils.get_page_obj(request, root_comments, user_context_instance.rows_per_page)
    # Načtení potomků pro každou kategorii
    #cache_tree_children(page_obj)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.discussion = Discussion.objects.get(id=diskuse_id)
            new_comment.created_by = request.user.username
            new_comment.ip_address = request.META.get("REMOTE_ADDR", None)
            new_comment.save()
        return redirect('comments', diskuse_id=str(diskuse_id))
    user_context_instance = utils.get_user_context_instance(request)
    context = {
        'form_comment': CommentForm(),
        'form_reply': CommentReplyForm(),
        'sort_by': sort_by,
        'diskuse_id': diskuse_id,
        'page_obj': page_obj,
        'total_pages': total_pages,
        'discussion': Discussion.objects.get(id=diskuse_id),
        'auto_show_all_replies': user_context_instance.auto_show_all_replies,
        'display_time': user_context_instance.display_time_difference,
    }
    return render(request, "comments/comments.html", context)

def comments_thread (request, diskuse_id, thread_id):
    #request.session['previous_url'] = request.META.get('HTTP_REFERER')
    utils.save_page(request)
    print (f"thread id {thread_id}")
    sort_by = request.GET.get('sort_by')
    user_context_instance = utils.get_user_context_instance(request)
    if sort_by == None:
        sort_by = user_context_instance.default_comments_ordering
    else:
        sort_by = int(sort_by)
    utils.save_user_context_instance(request, None, None,  sort_by)
    thread_comments = Comment.objects.filter(root_id=thread_id)
    if diskuse_id > 0:
        discussion = Discussion.objects.get(id=diskuse_id)
    else:
        discussion = None
    for elem in thread_comments:
        reply_comments = Comment.objects.filter(root_id = elem.root_id)
        cache_tree_children(reply_comments)
        elem.reply_comments = reply_comments
    page_obj = thread_comments
    print (f"vole: {thread_comments}")
    # Načtení potomků pro každou kategorii
    cache_tree_children(page_obj)
    user_context_instance = utils.get_user_context_instance(request)
    context = {
        'form_comment': CommentForm(),
        'sort_by': sort_by,
        'diskuse_id': diskuse_id,
        'thread_id': thread_id,
        'page_obj': page_obj,
        'discussion': discussion,
        'display_time': user_context_instance.display_time_difference,
    }
    return render(request, "comments/comments.html", context)

def user_comments(request, diskuse_id, username):
    #request.session['previous_url'] = request.META.get('HTTP_REFERER')
    utils.save_page(request)
    sort_by = request.GET.get('sort_by')
    user_context_instance = utils.get_user_context_instance(request)
    if sort_by == None:
        sort_by = user_context_instance.default_comments_ordering
    else:
        sort_by = int(sort_by)
    utils.save_user_context_instance(request, None, None,  sort_by)

    user = User.objects.get(username=username)
      ## comments = Comment.objects.filter(created_by=user, parent__isnull=True).order_by('-created_on')
      ##  discussion = Discussion.objects.get(id=diskuse_id)
      ##  comments_thread = Comment.objects.filter(created_by=user, discussion=discussion).order_by('-created_on')
    if sort_by==1:
        root_comments = Comment.objects.filter(created_by=user, parent__isnull=True).order_by('-created_on')
    elif sort_by==2:
        root_comments = Comment.objects.filter(created_by=user, parent__isnull=True).order_by('-replies_count')
    elif sort_by==3:
        root_comments = Comment.objects.filter(created_by=user, parent__isnull=True).order_by('-plus')

    page_obj, total_pages = utils.get_page_obj(
            request, root_comments, user_context_instance.rows_per_page)
    context = {
        'form_comment': CommentForm(),
        'sort_by': sort_by,
        'user': user,
        'diskuse_id': diskuse_id,
        'page_obj': page_obj,
        'total_pages': total_pages,
        'display_time': user_context_instance.display_time_difference,
    }
    return render(request, "comments/user_comments.html", context)


@login_required(login_url='/accounts/login')
def new_comment(request, diskuse_id):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.parent = None
            new_comment.discussion = Discussion.objects.get(id=diskuse_id)
            new_comment.created_by = request.user
            new_comment.ip_address = request.META.get("REMOTE_ADDR", None)
            new_comment.save()
            return redirect('comments', diskuse_id=str(diskuse_id))
    else:
        form = CommentForm()
    comments = Comment.objects.filter(
        discussion=diskuse_id, parent__isnull=False)
    context = {
        'form_comment': form,
        'comments': comments,
        'diskuse_id': diskuse_id,
    }
    return render(request, 'comments/comments.html', context)


def options_comment(request, diskuse_id, comment_id):
    user_context_instance = utils.get_user_context_instance(request)
    if request.method == 'POST':
        if 'cancel' in request.POST:
            return redirect('comments', diskuse_id=str(diskuse_id))
    else:
        form = CommentForm()
    sort_by = request.GET.get('sort_by')
    user_context_instance = utils.get_user_context_instance(request)
    if sort_by == None:
        sort_by = user_context_instance.default_comments_ordering
    else:
        sort_by = int(sort_by)
    utils.save_user_context_instance(request, None, None,  sort_by)
    if diskuse_id == 0:
        return redirect('home_discussions')
    else:
        discussion = Discussion.objects.get(id=diskuse_id)
    if sort_by==1:
        root_comments = Comment.objects.filter(discussion=discussion, parent__isnull=True).order_by('-created_on')
    elif sort_by==2:
        root_comments = Comment.objects.filter(discussion=discussion, parent__isnull=True).order_by('-replies_count')
    elif sort_by==3:
        root_comments = Comment.objects.filter(discussion=discussion, parent__isnull=True).order_by('-plus')
    for elem in root_comments:
        reply_comments = Comment.objects.filter(root_id = elem.root_id)
        cache_tree_children(reply_comments)
        elem.reply_comments = reply_comments

    page_obj, total_pages = utils.get_page_obj(request, root_comments, user_context_instance.rows_per_page)
  
    comment = Comment.objects.get(id=comment_id)
    context = {
        'form_comment': form,
        'options_comment': comment_id, #comment.parent.id,
        'page_obj': page_obj,
        'total_pages': total_pages,
        'sort_by': sort_by,
        'diskuse_id': diskuse_id,
       # 'root_id': comment.root_id,
        'discussion': Discussion.objects.get(id=diskuse_id),
        'auto_show_all_replies': user_context_instance.auto_show_all_replies,
        'display_time': user_context_instance.display_time_difference,
        }
    return render(request, 'comments/comments.html', context)

def options_comment_thread(request, diskuse_id, comment_id, thread_id):
    user_context_instance = utils.get_user_context_instance(request)
    if request.method == 'POST':
        if 'cancel' in request.POST:
            return redirect('comments', diskuse_id=str(diskuse_id))
    else:
        form = CommentForm()
    sort_by = request.GET.get('sort_by')
    user_context_instance = utils.get_user_context_instance(request)
    if sort_by == None:
        sort_by = user_context_instance.default_comments_ordering
    else:
        sort_by = int(sort_by)
    utils.save_user_context_instance(request, None, None,  sort_by)
    if diskuse_id == 0:
        return redirect('home_discussions')
    else:
        discussion = Discussion.objects.get(id=diskuse_id)
   
    thread_comments = Comment.objects.filter(root_id=thread_id)
    page_obj = thread_comments
    context = {
        'form_comment': form,
        'options_comment': comment_id, #comment.parent.id,
        'page_obj': page_obj,
        'sort_by': sort_by,
        'diskuse_id': diskuse_id,
        'thread_id': thread_id,
      #  'root_id': Comment.objects.get(id=comment_id).root_id,
        'discussion': discussion,
        'auto_show_all_replies': user_context_instance.auto_show_all_replies,
        'display_time': user_context_instance.display_time_difference,
        }
    return render(request, 'comments/comments.html', context)

@login_required(login_url='/accounts/login')
def reply_comment(request, diskuse_id, operation, comment_id):
    user_context_instance = utils.get_user_context_instance(request)
    root_id=Comment.objects.get(id=comment_id).root_id
    if request.method == 'GET':
        if operation == "delete":
            comment = Comment.objects.get(id=comment_id)
            try:
                comment.delete()
                messages.success(request, "Komentář byl úspěšně smazán.")
            except:
                messages.error(request, "Komentář nemůže být smazán.")
                print ("comment can not be deleted")
            #return redirect('comments', diskuse_id=str(diskuse_id))
            operation='none'
            form = CommentForm()
        else:
            form = CommentForm()
    elif request.method == 'POST':
        if 'cancel' in request.POST:
            form = CommentForm()
            operation='none'
            #return redirect('comments', diskuse_id=str(diskuse_id))
        elif 'reply' in request.POST: 
            form = CommentForm(request.POST)
            try:
                orig_comment =Comment.objects.get(id=comment_id)
            except:
                messages.error(request, "Původní komentář byl smazán")
                return redirect('comments', diskuse_id=str(diskuse_id))
            if form.is_valid():
                new_comment = form.save(commit=False)
                new_comment.discussion = Discussion.objects.get(id=diskuse_id)
                new_comment.parent = Comment.objects.get(id=comment_id)
                new_comment.created_by = request.user
                new_comment.ip_address = request.META.get("REMOTE_ADDR", None)
                try:
                    new_comment.save()
                except:
                    messages.error(request, "Reakce nemůže být uložena. Původní komentář byl smazán")
                operation='none'
                #return redirect('comments', diskuse_id=str(diskuse_id))
        elif 'edit' in request.POST: 
            form = CommentForm(request.POST)
            if form.is_valid():
               # new_comment = form.save(commit=False)
                comment = Comment.objects.get(id=comment_id)
                comment.content = form.cleaned_data['content']
                comment.ip_address = request.META.get("REMOTE_ADDR", None)
                comment.save()
                operation='none'
                #return redirect('comments', diskuse_id=str(diskuse_id))
    else:
        form = CommentForm()
    sort_by = request.GET.get('sort_by')
    user_context_instance = utils.get_user_context_instance(request)
    if sort_by == None:
        sort_by = user_context_instance.default_comments_ordering
    else:
        sort_by = int(sort_by)
    utils.save_user_context_instance(request, None, None,  sort_by)
    if diskuse_id == 0:
        return redirect('home_discussions')
    else:
        discussion = Discussion.objects.get(id=diskuse_id)
    if sort_by==1:
        root_comments = Comment.objects.filter(discussion=discussion, parent__isnull=True).order_by('-created_on')
    elif sort_by==2:
        root_comments = Comment.objects.filter(discussion=discussion, parent__isnull=True).order_by('-replies_count')
    elif sort_by==3:
        root_comments = Comment.objects.filter(discussion=discussion, parent__isnull=True).order_by('-plus')
    for elem in root_comments:
        reply_comments = Comment.objects.filter(root_id = elem.root_id)
        cache_tree_children(reply_comments)
        elem.reply_comments = reply_comments

    page_obj, total_pages = utils.get_page_obj(request, root_comments, user_context_instance.rows_per_page)
    if operation == "reply":
        context = {
        'form_comment': form,
        'form_reply': CommentReplyForm(),
        'reply_comment': comment_id,
        'page_obj': page_obj,
        'total_pages': total_pages,
        'sort_by': sort_by,
        'operation': "reply",
        'diskuse_id': diskuse_id,
        'root_id': Comment.objects.get(id=comment_id).root_id,
        'discussion': discussion,
        'display_time': user_context_instance.display_time_difference,
        }
    elif operation == "edit":
        comment = Comment.objects.get(id=comment_id)
        context = {
        'form_comment': form,
        'form_reply': CommentReplyForm(initial={'content':comment.content}),
        'reply_comment': comment_id, #comment.parent.id,
        'page_obj': page_obj,
        'total_pages': total_pages,
        'sort_by': sort_by,
        'operation': "edit",
        'diskuse_id': diskuse_id,
        'root_id': Comment.objects.get(id=comment_id).root_id,
        'discussion': discussion,
        'auto_show_all_replies': user_context_instance.auto_show_all_replies,
        'display_time': user_context_instance.display_time_difference,
        }
    elif operation == "none":
        context = {
        'form_comment': form,
        'page_obj': page_obj,
        'total_pages': total_pages,
        'sort_by': sort_by,
        'diskuse_id': diskuse_id,
        'root_id': root_id,
        'discussion': discussion,
        'auto_show_all_replies': user_context_instance.auto_show_all_replies,
        'display_time': user_context_instance.display_time_difference,
        }
    return render(request, 'comments/comments.html', context)



@login_required(login_url='/accounts/login')
def reply_comment_thread(request, operation, diskuse_id, comment_id, thread_id):
    user_context_instance = utils.get_user_context_instance(request)
    if request.method == 'GET':
        if operation == "delete":
            comment = Comment.objects.get(id=comment_id)
            try:
                comment.delete()
                messages.success(request, "Komentář byl úspěšně smazán.")
            except:
                messages.error(request, "Komentář nemůže být smazán.")
                print ("comment can not be deleted")
            return redirect('comments_thread', diskuse_id=str(diskuse_id), thread_id=thread_id)
        form = CommentForm()
    elif request.method == 'POST':
        if 'cancel' in request.POST:
            return redirect('comments_thread', diskuse_id=str(diskuse_id), thread_id=thread_id)
        elif 'reply' in request.POST:
            form = CommentForm(request.POST)
            if form.is_valid():
                new_comment = form.save(commit=False)
                new_comment.discussion = Discussion.objects.get(id=diskuse_id)
                new_comment.parent = Comment.objects.get(id=comment_id)
                new_comment.created_by = request.user
                new_comment.ip_address = request.META.get("REMOTE_ADDR", None)
                new_comment.save()
                return redirect('comments_thread', diskuse_id=str(diskuse_id), thread_id=thread_id)
        elif 'edit' in request.POST:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = Comment.objects.get(id=comment_id)
                comment.content = form.cleaned_data['content']
                comment.ip_address = request.META.get("REMOTE_ADDR", None)
                comment.save()
                return redirect('comments_thread', diskuse_id=str(diskuse_id), thread_id=thread_id)
    else:
        form = CommentForm()
    sort_by = request.GET.get('sort_by')
    user_context_instance = utils.get_user_context_instance(request)
    if sort_by == None:
        sort_by = user_context_instance.default_comments_ordering
    else:
        sort_by = int(sort_by)
    utils.save_user_context_instance(request, None, None,  sort_by)
    if diskuse_id == 0:
        return redirect('home_discussions')
    else:
        discussion = Discussion.objects.get(id=diskuse_id)
    thread_comments = Comment.objects.filter(root_id=thread_id)
    page_obj = thread_comments
    cache_tree_children(page_obj)
    if operation == "reply":
        context = {
        'form_comment': form,
        'form_reply': CommentReplyForm(),
        'reply_comment': comment_id,
        'root_id': Comment.objects.get(id=comment_id).root_id,
        'thread_id': thread_id,
        'page_obj': page_obj,
        'operation': 'reply',
        'diskuse_id': diskuse_id,
        'discussion': discussion,
        'auto_show_all_replies': user_context_instance.auto_show_all_replies,
        'display_time': user_context_instance.display_time_difference,
        }
    elif operation == "edit":
        comment = Comment.objects.get(id=comment_id)
        context = {
        'form_comment': form,
        'form_reply': CommentReplyForm(initial={'content':comment.content}),
        'reply_comment': comment_id, #comment.parent.id,
        'page_obj': page_obj,
        'thread_id': thread_id,
        'root_id': Comment.objects.get(id=comment_id).root_id,
        'operation': 'edit',
        'diskuse_id': diskuse_id,
        'discussion': discussion,
        'auto_show_all_replies': user_context_instance.auto_show_all_replies,
        'display_time': user_context_instance.display_time_difference,
        }
    return render(request, 'comments/comments.html', context)


