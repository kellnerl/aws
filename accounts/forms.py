from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
#from captcha.fields import ReCaptchaField



class RegistrationForm(UserCreationForm):
    email = forms.EmailField()
    born_on = forms.DateField(label='Narozen dne',required=True, help_text="Registrovat se může pouze osoba starší 15ti let. Proto uveďte své datum narození.", widget=forms.SelectDateWidget(years=range(1940, 2013),empty_label='Vyberte datum'))
    first_name=forms.CharField(label='Jméno:', required=True, widget=forms.TextInput(attrs={'class': 'input-font', 'placeholder':'Jméno'}))
    last_name=forms.CharField(label='Příjmení:', required=True, widget=forms.TextInput(attrs={'class': 'input-font',  'placeholder':'Příjmení'}))
    confirm=forms.BooleanField(label='Potvrzuji, že jsem uvedl pravdivé údaje',required=True)
    #captcha = ReCaptchaField()
  

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',  'password1', 'password2', 'born_on', 'confirm')

class MySetPasswordForm(SetPasswordForm):
   class Meta:
        model = User


class MyPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label='Email')

    def save(self, request, **kwargs):
        email = self.cleaned_data["email"]
        active_users = self.get_users(email)
        for user in active_users:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            user_email = user.email
            user_email = user_email.lower()
            subject = "Reset hesla"
            message = f"Reset hesla zde: {uid}/{token}"
            print("posílám email...")
            send_mail(subject, message, 'info@ipe.cz', [user_email], html_message=message)

            #user.email_user(subject, message)

