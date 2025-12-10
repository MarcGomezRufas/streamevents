# events/forms.py
from django import forms
from django.utils import timezone
from .models import Event, CATEGORY_CHOICES, STATUS_CHOICES

class DateTimeInput(forms.DateTimeInput):
    input_type = 'datetime-local'

class EventCreationForm(forms.ModelForm):
    scheduled_date = forms.DateTimeField(widget=DateTimeInput(attrs={'class':'form-control'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'rows':5,'class':'form-control'}))
    thumbnail = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class':'form-control'}))

    class Meta:
        model = Event
        fields = ['title','description','category','scheduled_date','thumbnail','max_viewers','tags','stream_url']
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control'}),
            'category': forms.Select(choices=CATEGORY_CHOICES, attrs={'class':'form-control'}),
            'max_viewers': forms.NumberInput(attrs={'class':'form-control','min':1,'max':1000}),
            'tags': forms.TextInput(attrs={'class':'form-control','placeholder':'música, indie, talk'}),
            'stream_url': forms.URLInput(attrs={'class':'form-control','placeholder':'https://youtu.be/... or https://www.twitch.tv/...'}),
        }

    def clean_scheduled_date(self):
        scheduled = self.cleaned_data['scheduled_date']
        if scheduled < timezone.now():
            raise forms.ValidationError("La data programada no pot ser en el passat.")
        return scheduled

    def clean_max_viewers(self):
        mv = self.cleaned_data.get('max_viewers', 100)
        if mv < 1 or mv > 1000:
            raise forms.ValidationError("El nombre màxim d'espectadors ha d'estar entre 1 i 1000.")
        return mv

    def clean_title(self):
        title = self.cleaned_data['title']
        # Únic per usuari: validation should be done in view where request.user is available
        return title


class EventUpdateForm(forms.ModelForm):
    scheduled_date = forms.DateTimeField(widget=DateTimeInput(attrs={'class':'form-control'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'rows':5,'class':'form-control'}))
    thumbnail = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class':'form-control'}))

    class Meta:
        model = Event
        fields = ['title','description','category','scheduled_date','thumbnail','max_viewers','tags','status','stream_url']
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control'}),
            'category': forms.Select(choices=CATEGORY_CHOICES, attrs={'class':'form-control'}),
            'status': forms.Select(choices=STATUS_CHOICES, attrs={'class':'form-control'}),
            'max_viewers': forms.NumberInput(attrs={'class':'form-control','min':1,'max':1000}),
            'tags': forms.TextInput(attrs={'class':'form-control'}),
            'stream_url': forms.URLInput(attrs={'class':'form-control'}),
        }

    def clean_max_viewers(self):
        mv = self.cleaned_data.get('max_viewers', 100)
        if mv < 1 or mv > 1000:
            raise forms.ValidationError("El nombre màxim d'espectadors ha d'estar entre 1 i 1000.")
        return mv

    def clean(self):
        cleaned = super().clean()
        # Nota: per validar 'només creador pot canviar l'estat' i 'no canviar data si està en directe'
        # necessitem la instància i l'usuari que sol·licita la modificació; això es comprovarà a la vista.
        return cleaned


class EventSearchForm(forms.Form):
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Cerca per títol o descripció'}))
    category = forms.ChoiceField(required=False, choices=[('','Totes')] + CATEGORY_CHOICES, widget=forms.Select(attrs={'class':'form-control'}))
    status = forms.ChoiceField(required=False, choices=[('','Tots')] + STATUS_CHOICES, widget=forms.Select(attrs={'class':'form-control'}))
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type':'date','class':'form-control'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type':'date','class':'form-control'}))
