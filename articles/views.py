
import re
import json
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from django.shortcuts import redirect, render
import requests
import utils
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from articles.forms import ArticleUserQueryForm
from articles.models import Article
from discussions.models import Discussion, Domain
from utils import get_page_obj, get_user_context_instance

# Create your views here.

def find_articles_on_idnes(key_word, articles, days_old):
    ret_articles = list(articles)
    # Vytvoříme URL vyhledávací stránky Idnes.cz s daným dotazem
    search_url = f"https://hledej.idnes.cz/clanky.aspx?q={key_word}"

    # Získáme obsah HTML stránky
    response = requests.get(search_url)
    html_content = response.text

    # Zpracujeme HTML obsah pomocí BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Najdeme všechny odkazy na články
    article_links = soup.find_all('a', {'class': 'title'})

    invisible_chars_regex = r'\s+'
    # Pro každý odkaz získáme URL článku a vytiskneme ho
    for link in article_links:
        article_url = link['href']
        article_title = re.sub(invisible_chars_regex, ' ', link.text)
        description_element = link.find_next('p')
        article_description = description_element.text.strip()
        tema_element = link.find_next(class_='cite')
        article_tema = tema_element.text.strip()
        time_element = link.find_next(class_='date')
        article_time = time_element.text.strip()
        try:
            parsed_date = datetime.strptime(article_time, '%d.%m.%Y %H:%M')   
        except: 
            parsed_date = datetime.strptime(article_time, '%d.%m.%Y')  
        day = parsed_date.day
        month = parsed_date.month
        year = parsed_date.year
        target_date = datetime(year=year, month=month, day=day)

        # Výpočet rozdílu mezi daty
        date_difference =  datetime.now() - target_date 

        # Definice prahu 10 dní
        threshold = timedelta(days=int(days_old))

         # Porovnání s prahem
        if date_difference <= threshold:
            discussion = Discussion.objects.filter(url=article_url).exists()
            if discussion:
                discussion_id = (Discussion.objects.filter(url=article_url)[0]).id
                comments_count = (Discussion.objects.filter(url=article_url)[0]).comments_count
            else:
                discussion_id = 0
                comments_count = 0
            article = Article(
            title=article_title, 
            url=article_url, 
            domain=urlparse(article_url).netloc,
            description=article_description, 
            published_on=target_date,
            theme=article_tema,
            discussion=discussion,
            discussion_id=discussion_id,
            comments_count=comments_count)  # Vytvoření fiktivního prvku             
            ret_articles.append(article)  # Přidání fiktivního prvku do seznamu 

    return ret_articles

def find_articles_on_seznam(key_word, articles, days_old, filter):
    ret_articles = list(articles)
    # Vytvoříme URL vyhledávací stránky Idnes.cz s daným dotazem
    search_url = f"https://search.seznam.cz/clanky/?q={key_word}&count=200"

    # Získáme obsah HTML stránky
    response = requests.get(search_url)
    response.encoding = 'utf-8'
    html_content = response.text


    # Zpracujeme HTML obsah pomocí BeautifulSoup
    #soup = BeautifulSoup(html_content, 'lxml')
    soup = BeautifulSoup(html_content, 'html.parser')

    # Najdeme všechny odkazy na články
    json_element = soup.find(id="renderer-state-data")
    json_text = json_element ['data-state']
    json_data = json.loads(json_text)
    json_sub = json_data["data"]
    json_sub = json_sub["entities"][0]
    json_sub = json_sub["subEntities"][2]
    json_subentities = json_sub["subEntities"]
    #print (json_subentities)
    for sb in json_subentities:
        if 'article' in sb['data'] and 'snippet' in sb['data']:
           # print (sb['data'])
            try:
                article_author = sb['data']['article']['author']
            except:
                article_author = None
            article_title = sb['data']['article']['title']
            article_description = sb['data']['article']['description']
            article_url = sb['data']['snippet']['url']
            article_domain=urlparse(article_url).netloc
            domains = Domain.objects.filter(section=filter).values_list('domain', flat=True)

            if filter >0 and not article_domain in domains:
                continue
            try:
                date_int = sb['data']['article']['publicationDate']
                print(date_int)
                dt = datetime.fromtimestamp(date_int)
                day = dt.day
                month = dt.month
                year = dt.year
                target_date = datetime(year=year, month=month, day=day)  

        # Výpočet rozdílu mezi daty
                date_difference =  datetime.now() - target_date 

                threshold = timedelta(days=int(days_old))

            except:
                continue
         # Porovnání s prahem
            if date_difference <= threshold:
                discussion = Discussion.objects.filter(url=article_url).exists()
                if discussion:
                    discussion_id = (Discussion.objects.filter(url=article_url)[0]).id
                    comments_count = (Discussion.objects.filter(url=article_url)[0]).comments_count
                else:
                    discussion_id = 0
                    comments_count = 0
                article = Article(
                title=article_title, 
                url=article_url, 
                domain=article_domain,
                description=article_description, 
                published_on=target_date,
                author=article_author,
                discussion=discussion,
                discussion_id=discussion_id,
                comments_count=comments_count)  # Vytvoření fiktivního prvku             
                ret_articles.append(article)  # Přidání fiktivního prvku do seznamu 

    return ret_articles

def new_article_query (request):
    pass

def article_search (request):
    utils.save_page(request)
    key_word = request.GET.get('key_word')
    section = request.GET.get('section')
    days_old = request.GET.get('days_old')

    if not days_old:
        days_old = 7
    if request.method == 'GET':
        form = ArticleUserQueryForm(request.GET)
        print (f"form.is_valid() {form.is_valid()}")
        if form.is_valid():
            key_word = form.cleaned_data['key_word']
            section = form.cleaned_data['section']
            lastperiod = form.cleaned_data['lastperiod']
            print(lastperiod)
      #  else:
      #      return redirect('article_search', request)
     
        articles = Article.objects.none()
        if section == 'iDnes':
            articles = find_articles_on_idnes(key_word, Article.objects.none(), days_old)
            articles.sort(key=lambda x: x.published_on, reverse=True)
        elif section == 'all':
            articles = find_articles_on_seznam(key_word, Article.objects.none(), days_old, filter=0)
            articles.sort(key=lambda x: x.published_on, reverse=True)
        elif section == 'seznam':
            articles = find_articles_on_seznam(key_word, Article.objects.none(), days_old, filter=4)
            articles.sort(key=lambda x: x.published_on, reverse=True)
        page_obj, total_pages = get_page_obj(request, articles, utils.get_user_context_instance(request).rows_per_page)
        form = ArticleUserQueryForm(initial={'key_word': key_word,'section': section, 'days_old': days_old})
        context = {
                'page_obj': page_obj,
                'articles': articles,
                'form': form,
                'key_word': key_word,
                'section': section,
                'days_old': days_old,
            }
        return render(request, "articles.html", context)

    form = ArticleUserQueryForm(initial={'key_word': key_word,'section':section, 'days_old': days_old})   
    context = {
                'form': form,
                'key_word': key_word,
                'section': section,
                'days_old': days_old,
            }
    return render(request, "articles.html", context)
    