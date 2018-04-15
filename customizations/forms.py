
from django import forms
from django.core.validators import FileExtensionValidator
from .models import Customization


class FormCustomization(forms.ModelForm):

    class Meta:
        model = Customization
        fields = ['name', 'select_event', 'logo', 'message', 'select_design_template', 'message_ticket']

    name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={'placeholder': 'name', 'class': 'form-control'}
        )
    )
    options_event = (('Apply All Events', 'apply_all'),)
    select_event = forms.ChoiceField(
        choices=options_event,
        widget=forms.Select(
            attrs={'class': 'form-control'}
        )
    )

    logo = forms.ImageField(
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg'])],
        widget=forms.FileInput(
            attrs={'class': 'form-control'}
        )
    )

    message = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={'placeholder': 'message body', 'class': 'form-control', 'rows': 6}
        )
    )

    options_design = (('DESIGN 1', 'design_one'),)
    select_design_template = forms.ChoiceField(
        choices=options_design,
        widget=forms.Select(
            attrs={'class': 'form-control'}
        )
    )
    message_ticket = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={'placeholder': 'message body', 'class': 'form-control', 'rows': 6}
        )
    )
