# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import FormView
from django.core.mail import BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import EmailMessage
from forms import FormEmailSend
from django.contrib.auth.mixins import LoginRequiredMixin


class ViewSendEmail(LoginRequiredMixin, FormView):
    form_class = FormEmailSend
    template_name = 'mail/email_send.html'

    def form_valid(self, form):
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']
        from_email = form.cleaned_data['from_email']
        to_email = form.cleaned_data['to_email']
        emails = []
        if ',' in to_email:
            for email in to_email.split(','):
                emails.append(email)
        else:
            emails.append(to_email)

        if 'send_email' in self.request.POST:
            send_email(subject, message, from_email, emails)
        return HttpResponseRedirect('/')


def send_email(subject, message, from_email, emails):
    email = EmailMessage(
        subject,
        message,
        from_email,
        emails,
        # ['bcc@example.com'],
        reply_to=['edacticket@gmail.com'],
        headers={'Message-ID': 'foo'},
    )
    # email.attach('design.png', img_data, 'image/png')
    email.attach_file('mail/tickets.png')
    if subject and message and from_email:
        try:
            email.send()
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        return HttpResponseRedirect('/')
    else:
        # In reality we'd use a form class
        # to get proper validation errors.
        return HttpResponse('Make sure all fields are entered and valid.')