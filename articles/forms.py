from django import forms
import requests

from articles.models import ArticleUserQuery
from discussions.models import ArticleTheme, Section



class ArticleUserQueryForm(forms.ModelForm):
    key_word=forms.CharField(label='Klíčové slovo', required=True, widget=forms.TextInput(attrs={'class': 'input-font', 'size':35, 'placeholder':'hledané klíčové slovo'}))
    #section=forms.CharField(label='Portál', required=False, widget=forms.TextInput(attrs={'class': 'input-font', 'size':20, 'placeholder':'jméno portálu'}))
    section = forms.ChoiceField(choices=[], label='Portál', required=False)
    days_old_choices = [('7', 'týden'),('14', '2 týdny'),('28', '4 týdny')]
    days_old = forms.ChoiceField(choices=days_old_choices, initial='14', label='Články za poslední', widget=forms.RadioSelect())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        scraped_sections = Section.objects.filter(scrapping=True)
        #section_choices = [('all', 'všechny')] + list(scraped_sections.values_list('name','name').order_by('name'))
        #section = forms.ChoiceField(choices=section_choices, label='Portál', required=False)

        # Načítání dat pro pole s možnými hodnotami až při inicializaci formuláře
        self.fields['section'].choices = [('all', 'všechny')] + list(scraped_sections.values_list('name','name').order_by('name'))
        

    class Meta:
        model = ArticleUserQuery
        # Uveďte pole, která chcete zahrnout do formuláře
        fields = ['key_word']
