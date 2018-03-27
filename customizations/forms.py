from django import forms
from django.core.validators import FileExtensionValidator

class FormCreateCustomization(forms.Form):
    options_event = (('Apply All Events', 'apply_all'),)
    select_event = forms.ChoiceField(choices=options_event)

    logo = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=['png','jpg'])])

    message = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={'placeholder': 'message body', 'class': 'form-control'}
        )
    )
    options_template = (('TEMPLATE 1', 'template_uno'),)
    select_ticket_template = forms.ChoiceField(choices=options_template)
