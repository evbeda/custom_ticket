from django import forms
from django.core.validators import FileExtensionValidator
from .models import Customization


class FormCustomization(forms.ModelForm):

    class Meta:
        model = Customization
        fields = [
            'name',
            'select_event',
            'logo',
            'message',
            'select_design_template',
            'message_ticket',
        ]

    name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'name',
                'class': 'form-control',
            }
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
            attrs={
                'placeholder': 'You can put here the email message.',
                'class': 'form-control',
                'rows': 6
            }
        )
    )

    options_design = (('DESIGN 1', 'Default Design'),)
    select_design_template = forms.ChoiceField(
        choices=options_design,
        widget=forms.Select(
            attrs={'class': 'form-control'}
        )
    )
    message_ticket = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={
                'placeholder': 'You can put here the ticket message',
                'class': 'form-control',
                'rows': 6
            }
        )
    )

    additional_info = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                'placeholder': 'addiional info here',
                'class': 'form-control',
                'rows': 6
            }
        )
    )

    footer_description = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'This inscription will be placed at the ticket bottom',
                'class': 'form-control',
                'rows': 1
            }
        )
    )

    show_event_sequence = forms.BooleanField(
        required=False,
        label="Show sequence of ticket by event",
    )

    show_ticket_type_sequence = forms.BooleanField(
        required=False,
        label="Show sequence of ticket by type",
    )

    show_ticket_type_price = forms.BooleanField(
        required=False,
        label="Show price of ticket purchased",
    )

    double_ticket = forms.BooleanField(
        required=False,
        label="Double Ticket",
    )
