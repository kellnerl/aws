from django import forms
import requests
from utils import remove_utm_parameters
from django.core.exceptions import ValidationError
from discussions.models import Comment
from discussions.models import Domain
from discussions.models import Discussion
from discussions.models import ArticleTheme


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

# comment creating a form
class CommentCopyLinkForm(forms.ModelForm):
    url=forms.CharField (label='',required=True, widget=forms.TextInput(attrs={'class': 'input-font','size': '42'}))
    comment=forms.CharField (label='',required=True, widget=forms.TextInput(attrs={'class': 'input-font','size': '42'}))
  
    class Meta:
        model = Comment
        fields = ['url']  # Uveďte pole, která chcete zahrnout do formuláře

# comment creating a form
class CommentForm(forms.ModelForm):
    content=forms.CharField (label='',required=True, widget=forms.Textarea(attrs={'rows': '6', 'cols':'96', 'size': '120', 'placeholder':'napište komentář k článku', 'class': 'custom-textarea'}))
  
    class Meta:
        model = Comment
        fields = ['content']  # Uveďte pole, která chcete zahrnout do formuláře

# comment reply a form
class CommentReplyForm(forms.ModelForm):
    content=forms.CharField (label='',required=False, widget=forms.Textarea(attrs={'rows': '6', 'cols':'72', 'size': '100', 'placeholder':'napište reakci ke komentáři', 'class': 'custom-textarea'}))
  
    class Meta:
        model = Comment
        fields = ['content']  # Uveďte pole, která chcete zahrnout do formuláře

class SearchDiscussionForm(forms.ModelForm):
    search_value = forms.CharField(max_length=340, widget=forms.TextInput(attrs={'class': 'input-font', 'size':70, 'placeholder':'Zadejte URL nebo titulek článku (část nebo celý)', 'style': 'border-color: rgb(71, 31, 182); border-width: 1px;border-radius: 2px; margin-left:1px;margin-right: 1px; height: 20px;'}))

    class Meta:
        model = Discussion
        fields = ['search_value']
        
class AdvancedSearchDiscussionForm(forms.ModelForm):
    title=forms.CharField( label='Titulek článku', required=False, widget=forms.TextInput(attrs={'class': 'input-font', 'size':45, 'placeholder':'hledaný text'}))
    author=forms.CharField(label='Autor článku', required=False, widget=forms.TextInput(attrs={'class': 'input-font', 'size':20, 'placeholder':'jméno autora článku'}))
    created_before = forms.DateField(label='před',required=False, widget=forms.SelectDateWidget())
    created_after  = forms.DateField(label='Diskuse vložena po',required=False, widget=forms.SelectDateWidget())
    last_comment_before = forms.DateField(label='před',required=False, widget=forms.SelectDateWidget())
    last_comment_after  = forms.DateField(label='Poslední příspěvek po',required=False,  widget=forms.SelectDateWidget())
    comments_count_min = forms.IntegerField(
        label='Počet příspěvků větší než',
        required=False,
        widget=forms.NumberInput(attrs={'min': 0, 'max': 1000, 'style': 'width: 50px;'})
    )
    #orderby_choices = [('1', 'dle času založení diskuze'),('2', 'dle počtu příspěvků'),('3', 'dle času posledního příspěvku')]
    #orderby = forms.ChoiceField(choices=orderby_choices, label='Seřadit dle', widget=forms.RadioSelect, required=True)
    active_field = forms.ChoiceField(choices=[('', '---------'), ('1', 'jen aktivní'), ('0', 'jen neaktivní')], initial='1', label='Status diskuse', required=False, widget=forms.Select(attrs={'style': 'font-size: 16px;'}))
    domain_field = forms.ChoiceField(choices=[],label='Doména', required=False, widget=forms.Select(attrs={'style': 'font-size: 16px;'}))
    theme_field = forms.ChoiceField(choices=[], label='Téma', required=False, widget=forms.Select(attrs={'style': 'font-size: 16px;'}))
     #active = forms.BooleanField (label='Aktivní diskuse', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Načítání dat pro pole s možnými hodnotami až při inicializaci formuláře
        self.fields['domain_field'].choices = [('', '---------')] + list(Domain.objects.values_list('domain','domain'))
        #self.fields['theme_field'].choices = [('', '---------')] + list(ArticleTheme.objects.values_list('id','name'))
        self.fields['theme_field'].choices = list(ArticleTheme.objects.values_list('id','name'))

    class Meta:
        model = Discussion
        # Uveďte pole, která chcete zahrnout do formuláře
        fields = ['title', 'author', 'comments_count_min','domain_field', 'theme_field', 'created_before', 'created_after', 'last_comment_before', 'last_comment_after','active_field']  


# discussion creating a form
class CreateDiscussionForm(forms.ModelForm):
    title=forms.CharField(label='Titulek', max_length=400, widget=forms.TextInput(attrs={'class': 'input-font', 'size':72, 'placeholder':'titulek článku'}))
    url=URLField(label='URL', max_length=400, widget=forms.TextInput(attrs={'class': 'input-font', 'size':72, 'placeholder':'url článku','readonly': True}))
    author=forms.CharField(label='Autor článku', required=False, widget=forms.TextInput(attrs={'class': 'input-font', 'size':28, 'placeholder':'jméno autora článku'}))
    theme_field = forms.ChoiceField(choices=[], label='Téma', required=False, widget=forms.Select(attrs={'style': 'font-size: 16px;'}))

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Načítání dat pro pole s možnými hodnotami až při inicializaci formuláře
        self.fields['theme_field'].choices = [('', '---------')] + list(ArticleTheme.objects.filter(id__gt=1).values_list('id','name'))


    class Meta:
        model = Discussion
        fields = ['title', 'url', 'author']

    def clean_url(self):
        url = self.cleaned_data['url']
        # Kontrola existence URL
        response = requests.head(url)
        if response.status_code != 200:
            raise forms.ValidationError('Neplatná URL.', 'invalid_url')

        # Kontrola unikátnosti URL v modelu Article
        if url:
            if Discussion.objects.filter(url=url).exists():
                raise forms.ValidationError('Tato URL již existuje.', 'article_exists')
        return remove_utm_parameters(url)
    
    def save(self, commit=True):
        instance = super().save(commit=commit)
        
        # Create and save Model Diskuse
        
        return instance
    
   
