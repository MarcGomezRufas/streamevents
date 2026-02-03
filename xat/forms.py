# xat/forms.py
from django import forms
from .models import XatMessage

OFFENSIVE_WORDS = ['caca', 'pedo', 'culo', 'pis', 'idiota', 'imbécil', 'gilipollas', 'puta', 'zorra', 'cabrón', 'mierda', 'joder', 'coño']

class XatMessageForm(forms.ModelForm):
    class Meta:
        model = XatMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Escriu un missatge...',
                'maxlength': 500
            })
        }

    def clean_message(self):
        msg = self.cleaned_data['message'].strip()
        if not msg:
            raise forms.ValidationError("El missatge no pot estar buit.")
        if len(msg) > 500:
            raise forms.ValidationError("Màxim 500 caràcters.")
        if any(word in msg.lower() for word in OFFENSIVE_WORDS):
            raise forms.ValidationError("Conté paraules inapropiades.")
        return msg