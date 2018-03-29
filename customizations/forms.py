
from django import forms
from django.core.validators import FileExtensionValidator


class FormCreateCustomization(forms.Form):
    options_event = (('Apply All Events', 'apply_all'),)
    select_event = forms.ChoiceField(choices=options_event,
         widget=forms.Select(
            attrs={'class': 'form-control'}
        )
    )

    logo = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg'])],
         widget=forms.FileInput(
            attrs={'class': 'form-control'}
        )
    )

    message = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={'placeholder': 'message body', 'class': 'form-control'}
        )
    )
    options_template = (('TEMPLATE 1', 'template_uno'),)
    select_ticket_template = forms.ChoiceField(choices=options_template,
         widget=forms.Select(
            attrs={'class': 'form-control'}
        )
    )


class FormSendEmailPreview(forms.Form):
    email_send = forms.EmailField(
        required=True,
        widget=forms.TextInput(
            attrs={'placeholder': 'email@gmail.com', 'class': 'form-control'}
        )
    )
