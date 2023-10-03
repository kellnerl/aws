from django import forms
import requests
from django.core.exceptions import ValidationError
from django.forms.models import inlineformset_factory
from .models import UserContext, UserSection, UserSectionDomain


class URLExistsValidator:
    def __call__(self, value):
        try:
            response = requests.head(value)
            if response.status_code != 200:
                raise  ValidationError("The URL does not exist.")
        except requests.exceptions.RequestException:
            raise ValidationError("An error occurred while checking the URL.")

class URLField(forms.URLField):
    default_validators = [URLExistsValidator()]


class UserDetailForm(forms.ModelForm):
    photo=forms.ImageField(label='Fotografie',required=False, widget=forms.FileInput(attrs={'class': 'custom-file-input'}))
    about_me=forms.CharField(label='Něco o mně', required=False, widget=forms.Textarea(attrs={'rows': '4', 'placeholder':'stručná charakteristika vaší osobnosti'}))
    sex_choice=[('M', 'Muž'), ('F', 'Žena'), ('N', 'Nechci sdělit')]
    sex=forms.ChoiceField(label='Pohlaví',choices=sex_choice, widget=forms.RadioSelect, required=False)
    place_of_residence=forms.CharField(label='Bydliště', required=False)
    class Meta:
        model = UserContext
        # Uveďte pole, která chcete zahrnout do formuláře
        fields = ['photo', 'about_me', 'place_of_residence', 'sex']


# user-context updating a form
class UserContextForm(forms.ModelForm):
    
    rows_per_page=forms.IntegerField(label='Počet zobrazených záznamů na stránce', required=True, min_value=3, max_value=20)
    #display_fullname=forms.BooleanField(label='Zobrazovat plné jméno místo přihlašovacího jména',required=False)
    display_time_difference=forms.BooleanField(label='Zobrazovat absolutní čas místo časového intervalu',required=False)
    auto_show_all_replies=forms.BooleanField(label='Automaticky zobrazit všechny odpovědi v diskusi',required=False)
    #notify_on_comment=forms.BooleanField(label='Posílat denní notifikaci ohledně komentářů na mé oblíbené diskuse',required=False)
    #notify_on_discussion=forms.BooleanField(label='Posílat denní notifikaci ohledně reakcí na moje příspěvky',required=False)
    #notify_on_favorite=forms.BooleanField(label='Posílat denní notifikaci ohledně komentářů oblíbeného uživatele',required=False)

    class Meta:
        model = UserContext
        # Uveďte pole, která chcete zahrnout do formuláře
        fields = ['rows_per_page', 'auto_show_all_replies', 'display_time_difference']

class UserSectionForm(forms.ModelForm):       
    name=forms.CharField(label='Jméno sekce', required=True, widget=forms.TextInput(attrs={'class': 'input-font', 'size':40, 'placeholder':'název sekce'}))
    description=forms.CharField(label='Popis sekce', required=False, widget=forms.Textarea(attrs={'rows': '4', 'placeholder':'popis, účel a charakteristika sekce'}))

    class Meta:
        model = UserSection
        # Uveďte pole, která chcete zahrnout do formuláře
        fields = ['name', 'description']
        labels = {'name':'Jméno sekce', 'description':'Popis'}
        exclude = ()

class UserSectionDomainForm(forms.ModelForm):       

    class Meta:
        model = UserSectionDomain
        # Uveďte pole   
        fields = ['domain']
        labels = {'domain':'Doména'}
        exclude = ()


UserDomainFormSet = inlineformset_factory(UserSection, UserSectionDomain, form=UserSectionDomainForm, extra=1)
