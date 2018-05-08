from django import forms
from django.core.validators import FileExtensionValidator
from .models import (
    Customization,
    BaseTicketTemplate,
)


class FormBaseTickets(forms.ModelForm):
    class Meta:
        model = BaseTicketTemplate
        fields = [
            'name',
            'template_source',
            'preview',
            'content_html'
        ]
    name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Name of base tickets',
                'class': 'form-control',
                'value': 'Default design',
            }
        )
    )
    template_source = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Source URL ticket template',
                'class': 'form-control',
                'value': 'tickets/template_default.html',
            }
        )
    )

    preview = forms.ImageField(
        required=True,
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg'])],
        widget=forms.FileInput(
            attrs={'class': 'form-control'}
        )
    )

    content_html = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={
                'placeholder': 'You can put here the html content.',
                'class': 'form-control',
                'rows': 6
            }
        )
    )


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
            'image_partner',
            'pdf_ticket_attach'
        ]

    name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Name to identify the customization',
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
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg'])],
        widget=forms.FileInput(
            attrs={'class': 'form-control'}
        )
    )

    message = forms.CharField(
        required=False,
        max_length=800,
        widget=forms.Textarea(
            attrs={
                'placeholder': 'e.g. Thanks for registering please keep your tickets handy. Print them out and bring them with you',
                'class': 'form-control',
                'rows': 6
            }
        )
    )
    tickets_templates = BaseTicketTemplate.objects.all()
    # options_design = (('DESIGN 1', 'Default Design'),)
    select_design_template = forms.IntegerField(widget=forms.HiddenInput())
    message_ticket = forms.CharField(
        required=True,
        max_length=400,
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Tell your attendees what they should bring the event, or specific info that they may need.',
                'class': 'form-control',
                'rows': 6
            }
        )
    )

    additional_info = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Add a partner description, useful information for your attendees or whatever you want to.',
                'class': 'form-control',
                'rows': 6
            }
        )
    )

    footer_description = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'placeholder': ' e.g. Eventbrite Inc. /  Reg. No. 4742147',
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

    hide_ticket_type_price = forms.BooleanField(
        required=False,
        label="Hide price of ticket purchased",
    )

    double_ticket = forms.BooleanField(
        required=False,
        label="Double Ticket",
    )
    image_partner = forms.ImageField(
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg'])],
        widget=forms.FileInput(
            attrs={'class': 'form-control'}
        )
    )
    TRUE_FALSE_CHOICES = (
        (True, 'Yes'),
        (False, 'No')
    )

    pdf_ticket_attach = forms.ChoiceField(choices=TRUE_FALSE_CHOICES, label="PDF Ticket Attach",
                                          initial='', widget=forms.Select(), required=True)
