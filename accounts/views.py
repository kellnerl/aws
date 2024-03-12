from django.forms import ValidationError
from django.http import Http404, HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse_lazy
from django.db.models import Q

from users.models import UserDetail

from .forms import MyPasswordResetForm, MySetPasswordForm, RegistrationForm
import utils
from datetime import datetime


# Create your views here.

class MyPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset.html'
    email_template_name = 'registration/password_reset_email.html'  # Šablona pro e-mail
    subject_template_name = 'registration/password_reset_subject.txt'  # Předmět e-mailu
    success_url = reverse_lazy('reset/done')
    form_class = MyPasswordResetForm  # Vlastní formulář pro reset hesla
    token_generator = default_token_generator  # Vlastní token generator, pokud potřebujete úpravy

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'E-mail s instrukcemi pro reset hesla byl odeslán.')
        return response

class MyPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'  # Změňte cestu k vaší šabloně

class MyPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'  # Změňte cestu k vaší šabloně
    success_url = 'password_reset_complete'

class MyPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'  # Změňte cestu k vaší šabloně



class LoginInterfaceView(LoginView):
    template_name = 'login.html'


class LogoutInterfaceView(LogoutView):
    def post(self, request, *args, **kwargs):
        self.logout(request)
        return redirect('home_discussions')


def custom_logout(request):
    logout(request)
    return redirect('home_discussions')

def registration_done(request, username):
    return render(request, 'registration/registration_done.html', {})

def activation_failure(request):
    return render(request, 'activation/activation_failure.html', {})

def activation_success(request):
    return render(request, 'activation/activation_success.html', {})


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            users=User.objects.filter(email=email)
            if users:
                messages.error(request, f"Účet se zadaným emailem již existuje! Použijte jiný email.")
            else:
                datum_narozeni = form.cleaned_data['born_on']
                aktualni_datum = datetime.now()
                age = aktualni_datum.year - datum_narozeni.year - ((aktualni_datum.month, aktualni_datum.day) < (datum_narozeni.month, datum_narozeni.day))
                if age<15:
                    messages.error(request, f"Věk {age} let neodpovídá požadavkům. Ukončete registraci!")
                else:
                    user = form.save(commit=False)
                    user.is_active = False
                    user.is_active = True ### pouze dočasně dokud není https
                    user.save()
                    userDetail = UserDetail.objects.get(user=user)
                    userDetail.born_on = datum_narozeni
                    userDetail.save()

            # Generování potvrzovacího tokenu
                    token = default_token_generator.make_token(user)

            # Vytvoření potvrzovacího e-mailu
                    current_site = get_current_site(request)
                    mail_subject = 'Aktivace účtu na diskuze.cz'
                    message = render_to_string('activation/activation_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': token,
                    })
                    print("posílám email...")
                    send_mail(mail_subject, message, 'info@ipe.cz', [user.email], html_message=message)

                    return redirect('registration_done', username=user.username)
        else:
            print("form není validní {form}")
    else: 
        form = RegistrationForm()

    return render(request, 'registration/register.html', {'form': form, 'central': True})

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('activation_success')
    else:
        return redirect('activation_failure')
    

