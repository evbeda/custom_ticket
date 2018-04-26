
from django import forms
from django.core.validators import FileExtensionValidator
from .models import Customization, BaseTicketTemplate


class FormCustomization(forms.ModelForm):

    class Meta:
        model = Customization
        fields = ['name', 'select_event', 'logo', 'message', 'message_ticket']

    name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={'placeholder': 'name', 'class': 'form-control'}
        )
    )
    options_event = (('Apply All Events', 'Apply to All'),)
    select_event = forms.ChoiceField(
        choices=options_event,
        widget=forms.Select(
            attrs={'class': 'form-control'}
        )
    )

    logo = forms.ImageField(
        required=True,
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

    tickets_templates = BaseTicketTemplate.objects.all()
    # select_design_template = forms.ChoiceField(choices=MY_CHOICES)

    message_ticket = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={'placeholder': 'message body', 'class': 'form-control', 'rows': 6}
        )
    )
