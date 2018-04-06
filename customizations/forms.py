
from django import forms
from django.core.validators import FileExtensionValidator
from events.models import Customization


class FormCustomization(forms.ModelForm):

    class Meta:
        model = Customization
        fields = ['select_event', 'logo', 'message', 'select_ticket_template']

    options_event = (('Apply All Events', 'apply_all'),)
    select_event = forms.ChoiceField(
        choices=options_event,
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
    select_ticket_template = forms.ChoiceField(
        choices=options_template,
        widget=forms.Select(
            attrs={'class': 'form-control'}
        )
    )



