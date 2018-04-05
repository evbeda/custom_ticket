from django import forms


class FormEmailSend(forms.Form):
    to_email = forms.EmailField(
        required=True,
        widget=forms.TextInput(
            attrs={'placeholder': 'Email to send to', 'class': 'form-control'}
        )
    )
    subject = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={'placeholder': 'subject', 'class': 'form-control'}
        )
    )
    message = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={'placeholder': 'Email body', 'class': 'form-control'}
        )
    )
    from_email = forms.EmailField(
        required=True,
        widget=forms.TextInput(
            attrs={'placeholder': 'Your Email', 'class': 'form-control'}
        )
    )


class FormSendEmailPreview(forms.Form):
    email_send = forms.EmailField(
        required=True,
        widget=forms.TextInput(
            attrs={'placeholder': 'email@gmail.com', 'class': 'form-control'}
        )
    )
