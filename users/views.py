from django.forms import ValidationError
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse_lazy
from django.db.models import Q
from django.db import transaction
from discussions.models import Domain, Section, Comment
from .forms import UserDomainFormSet
from django.forms.models import inlineformset_factory
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

import utils

from .forms import UserDetailForm, UserContextForm, UserSectionForm
from .models import UserDetail, UserContext, UserSection, UserSectionDomain

# Create your views here.

UserDomainFormSet = inlineformset_factory(UserSection, UserSectionDomain, fields=('domain',))


def get_user_context_instance (request):
    if request.user.is_anonymous:
        if UserContext.objects.filter(ip_address=request.META.get("REMOTE_ADDR", None)).exists():
            user_context_instance = UserContext.objects.get(ip_address=request.META.get("REMOTE_ADDR", None))
        else:
            user_context_instance = UserContext()
            user_context_instance.save()  
    else:   
        if UserContext.objects.filter(user=request.user).exists():
            user_context_instance = UserContext.objects.get(user=request.user)
        else:
            user_context_instance = UserContext()
            user_context_instance.save()
    return user_context_instance

@login_required(login_url='/login')
def user_info(request, username):
    #request.session['previous_url'] = request.META.get('HTTP_REFERER')
    utils.save_page(request)
    user_id = User.objects.filter(username=username) [0]
    userDetail=UserDetail.objects.filter(user=user_id)[0]
    from datetime import datetime
# Předpokládejme, že datum_narozeni je instance datetime objektu
    if userDetail.born_on:
        datum_narozeni = userDetail.born_on
# Získání aktuálního data
        aktualni_datum = datetime.now()
# Výpočet věku
        age = aktualni_datum.year - datum_narozeni.year - ((aktualni_datum.month, aktualni_datum.day) < (datum_narozeni.month, datum_narozeni.day))
    else:
        age = None
    comment_count = Comment.objects.filter(created_by=request.user, parent__isnull=True).count()
    reply_count = Comment.objects.filter(created_by=request.user, parent__isnull=False).count()
    context = {
                'userdetail':userDetail, 
                'age':age, 
                'comment_count':comment_count,
                'reply_count':reply_count,
            }
    return render(request, 'user/user_info.html', context)

@login_required(login_url='/login')
def user_detail(request, userid):
    #request.session['previous_url'] = request.META.get('HTTP_REFERER')
    utils.save_page(request)
    if request.method == 'POST':
        instance = get_object_or_404(UserDetail, user=request.user)
        form = UserDetailForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            userDetail = form.save(commit=False)
            userDetail.sex = form.cleaned_data['sex']
            userDetail.about_me = form.cleaned_data['about_me']
            userDetail.place_of_residence = form.cleaned_data['place_of_residence']
         #   image_file=form.cleaned_data['photo']
         #   userDetail.photo.save(image_file)
            userDetail.photo=form.cleaned_data['photo']
            userDetail.save()
            return redirect('user_info', request.user.username)
    else:
        instance = get_object_or_404(UserDetail, user=request.user)
    form = UserDetailForm(instance=instance)
    userDetail=UserDetail.objects.filter(user=request.user)[0]
    return render(request, 'user/user_detail.html', {'form': form,  'userdetail': userDetail, 'userid':userid})

@login_required(login_url='/login')
def user_context(request, userid):
    usersection_number = int(request.GET.get('usertab', '1'))
    section_name = request.GET.get('predeftab', '_')
    if not usersection_number:
        usersection_number = 1
    if not section_name:
        section_name = "_"
    print (f"request.method {request.method}")
    #request.session['previous_url'] = request.META.get('HTTP_REFERER')
    if request.method == 'GET':
        op = request.GET.get('op', None)
        print(op)
        if op == 'd':
            sections = UserSection.objects.filter(user=request.user).order_by('number')
            if usersection_number==0:
                usersection_number=1
            user_section1 = sections.filter (number=usersection_number)[0]
            user_section1 = UserSection.objects.get(id=user_section1.id)
            try:
                with transaction.atomic():
                    user_section1.delete()
                    usersections = UserSection.objects.filter(user=request.user).order_by('number')
                    i = 0
                    for section_obj in usersections:
                        i = i+1
                        section_obj.number = i
                        section_obj.save()
                    usersection_number = usersection_number-1
                #    return redirect('user_context', userid=userid, usersection_number=usersection_number,section_name=section_name)
            except Exception as e:
                pass
            section_name = "_"          
        elif op == 'a':
            if section_name == '_':
                excluded_names = UserSection.objects.filter(user=request.user).values_list('name',flat=True)
                print (excluded_names)
                #sections = Section.objects.exclude(name__in=excluded_names).values('name','name').order_by('number')
                section_obj = Section.objects.exclude(name__in=excluded_names).order_by('number')[0]
            else:
                section_obj=Section.objects.filter(name=section_name)[0]
            number = UserSection.objects.filter(user=request.user).count() + 1
            usersection = UserSection.objects.create(user=request.user, name=section_obj.name, type=section_obj.type, description=section_obj.description, number=number)    
            usersection_number = number
            excluded_names = UserSection.objects.filter(user=request.user).values_list('name',flat=True)
            sections = Section.objects.exclude(name__in=excluded_names).order_by('number')
            if sections:
                section_name = (sections[0]).name
            else:
                section_name = "_"     
        #    return redirect('user_context', userid=userid, usersection_number=usersection_number,section_name=section_name)
    
        elif op == 'g':
            sections = UserSection.objects.filter(user=request.user).order_by('number')
            user_section1 = sections.filter (number=usersection_number)[0]
            user_section2 = sections.filter (number=usersection_number+1)[0]
            user_section1.number=user_section1.number+1
            user_section2.number=user_section2.number-1
            try:
                with transaction.atomic():
                    user_section1.save()
                    user_section2.save()
                    usersection_number = user_section1.number
             #       return redirect('user_context', userid=userid)
             #       return redirect('user_context', userid=userid, usersection_number=usersection_number,section_name=section_name)

            except Exception as e:
                pass
        elif op == 'l':
            sections = UserSection.objects.filter(user=request.user).order_by('number')
            user_section1 = sections.filter (number=usersection_number)[0]
            user_section2 = sections.filter (number=usersection_number-1)[0]
            user_section1.number=user_section1.number-1
            user_section2.number=user_section2.number+1
            try:
                with transaction.atomic():
                    user_section1.save()
                    user_section2.save()
                    usersection_number = user_section1.number
                #    return redirect('user_context', userid=userid)
                #    return redirect('user_context', userid=userid, usersection_number=usersection_number,section_name=section_name)
            except Exception as e:
                pass
        print(op)
        instanceContext = get_object_or_404(UserContext, user=request.user)
        form = UserContextForm(instance=instanceContext)
    elif request.method == 'POST':
        instanceContext = get_object_or_404(UserContext, user=request.user)
        instanceDetail = get_object_or_404(UserDetail, user=request.user)
        form = UserContextForm(request.POST, instance=instanceContext)
        if form.is_valid():
            userContext = form.save(commit=False)
            userContext.rows_per_page = form.cleaned_data['rows_per_page']
            #userContext.display_fullname = form.cleaned_data['display_fullname'] 
            if userContext.display_fullname:
                if instanceDetail.last_name:
                    userContext.displayed_username = instanceDetail.first_name+" "+instanceDetail.last_name
            else:
                userContext.displayed_username = request.user.username
            userContext.display_time_difference = form.cleaned_data['display_time_difference']
            userContext.auto_show_all_replies = form.cleaned_data['auto_show_all_replies']
           # userContext.notify_on_comment = form.cleaned_data['notify_on_comment']
           # userContext.notify_on_discussion = form.cleaned_data['notify_on_discussion']
           # userContext.notify_on_favorite = form.cleaned_data['notify_on_favorite']
            userContext.save()
            #return redirect('navigate_back')
    else:
        instanceContext = get_object_or_404(UserContext, user=request.user)
        form = UserContextForm(instance=instanceContext)
        utils.save_page(request)
    user_sections = UserSection.objects.filter(user=request.user).order_by('number')
    print (user_sections)
    if user_sections:
        if usersection_number==0:
            usersection_number=1
        usersection_name = (user_sections.filter(number=usersection_number)[0]).name
        usersection_title = (user_sections.filter(number=usersection_number)[0]).title
        usersection_type = (user_sections.filter(number=usersection_number)[0]).type
        usersection_id = (user_sections.filter(number=usersection_number)[0]).id
    else:
        usersection_name = ""
        usersection_title = ""  
        usersection_number = 0
        usersection_type = ""
        usersection_id = 0
    excluded_names = UserSection.objects.filter(user=request.user).values_list('name',flat=True)
    print (excluded_names)
    #sections = Section.objects.exclude(name__in=excluded_names).values('name','name').order_by('number')
    sections = Section.objects.exclude(name__in=excluded_names).order_by('number')
    print (f"sections: {sections}")
    if sections:
        if not section_name or section_name=='_':
            section_name = (sections[0]).name
        print(f"section_name: {section_name}")
        section_obj=Section.objects.filter(name=section_name)[0]
        domains = Domain.objects.filter(section=section_obj)
    else:
        domains = None
        section_name = "_"
    
    context = {
        'form': form,
        'userid': userid,
        'user_section_number': usersection_number,
        'user_section_name': usersection_name,
        'user_section_title': usersection_title,
        'user_section_type': usersection_type,
        'user_section_id': usersection_id,
        'user_sections': user_sections,
        'section_name': section_name,
        'sections': sections,
        'domains': domains,
    }
    return render(request, 'user/user_context.html', context)

@login_required(login_url='/login')
def user_section_operation(request, userid, section, operation):
    return render(request, 'user/user_context.html')

@login_required(login_url='/login')
def user_section_edit(request, userid, section):
    if request.method == 'POST':
        form = UserDetailForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'user/user_context.html', context)
    userContext=UserContext.objects.filter(user=request.user)[0]
    sections = UserSection.objects.filter(user=userContext).order_by('number')
    user_section = sections.filter (number=section)[0]
    domains = UserSectionDomain.objects.filter(userSection=user_section)

    form = UserSectionForm(initial={'name':user_section.name, 'decription':user_section.description})
    context = {
        'form': form,
        'userid': userid,
        'section': section,
        'section_domains': domains, 
    }
    return render(request, 'user/usersection_form.html', context)


def user_section_domains(request, usersectionid):
    UserDomainFormSet = inlineformset_factory(UserSection, UserSectionDomain, fields=('domain',))

    userSection = UserSection.objects.get(pk=usersectionid)
    formset = UserDomainFormSet(instance=userSection)

    if request.method == 'POST':
        formset = UserDomainFormSet(request.POST, instance=userSection)
        if formset.is_valid():
            formset.save()

    return render(request, 'user/user_domains.html', {'formset': formset})

def user_section_new(request, userid, number):

    if request.method == 'POST':
        print("POST")
        form = UserSectionForm(request.POST)
        if form.is_valid():
            print("form valid")
            userSection = form.save(commit=False)
            userSection.user = request.user
            userSection.type = 'D'
            userSection.number = number + 1 
            userSection.save()
        else:
            print("form not valid")
    form = UserSectionForm()
    usersection = UserSection.objects.all()[0]
    context = {
        'form': form,
        'userid': userid,
        'usersectionid': usersection.id,
    }
    return render(request, 'user/usersection_form.html', context)


class UserSectionList(ListView):
    model = UserSection
    fields = ['name', 'description']
    labels = {'name': 'Jméno sekce','description': 'Popis',}

class UserSectionCreate(CreateView):
    model = UserSection
    fields = ['name', 'description']
    labels = {'name': 'Jméno sekce','description': 'Popis',}

class UserSectionDomainCreate(CreateView):
    model = UserSection
    fields = ['name', 'description']
    labels = {'name': 'Jméno sekce','description': 'Popis',}
   
    def get_success_url(self):
        #return reverse_lazy('user_context', args=[self.request.user.id, 0, '_'])
        return reverse_lazy('user_context', args=[self.request.user.id])   

    def get_context_data(self, **kwargs):
        data = super(UserSectionDomainCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['domains'] = UserDomainFormSet(self.request.POST)
            data['number'] = UserSection.objects.filter(user=self.request.user).count()
            data['user'] = self.request.user 
        else:
            data['domains'] = UserDomainFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        domains = context['domains']
        user = context['user']
        number = context['number']
        with transaction.atomic():
         #   self.object = form.save()
            self.object = form.save(commit=False)
            self.object.user = user
            self.object.type = 'D'
            self.object.number = number + 1 
            self.object = form.save()
            if domains.is_valid():
                domains.instance = self.object
                domains.save()
            
        return super(UserSectionDomainCreate, self).form_valid(form)


class UserSectionUpdate(UpdateView):
    model = UserSection
    success_url = '/'
    fields = ['name', 'description']
    labels = {'name': 'Jméno sekce','description': 'Popis',}

class UserSectionDomainUpdate(UpdateView):
    model = UserSection
    fields = ['name', 'description']
    labels = {'name': 'Jméno sekce','description': 'Popis',}
   # success_url = reverse_lazy('user_context', self.request.user.id, 0, '_')

    def get_success_url(self):
        #return reverse_lazy('user_context', args=[self.request.user.id, 0, '_'])
        return reverse_lazy('user_context', args=[self.request.user.id])

    def get_context_data(self, **kwargs):
        data = super(UserSectionDomainUpdate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['domains'] = UserDomainFormSet(self.request.POST, instance=self.object)
        else:
            data['domains'] = UserDomainFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        domains = context['domains']
        with transaction.atomic():
            self.object = form.save()

            if domains.is_valid():
                domains.instance = self.object
                domains.save()
        return super(UserSectionDomainUpdate, self).form_valid(form)


class UserSectionDelete(DeleteView):
    model = UserSection
    success_url = reverse_lazy('user_context', 0, '_')
