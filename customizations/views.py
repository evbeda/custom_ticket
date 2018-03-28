# -*- coding: utf-8 -*-
import datetime
import mimetypes
from core.utils import PDF
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse as r
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from django.views.generic import View, FormView
from events.models import Customization, TicketTemplate, EmailConfirmation
from .forms import FormCreateCustomization


def generate_pdf(request):
    data = {
        'today': datetime.date.today(),
        'type': 'VIP',
        'customer_name': 'Name ABC',
        'order_id': 1233434,
    }
    ticket_pdf = PDF('tickets/template_default.html', [data]).render()
    # return ticket_pdf.getvalue()
    return HttpResponse(ticket_pdf, content_type='application/pdf')


class PrintPdf(View):
    def get(self, request, *args, **kwargs):
        ticket_pdf = generate_pdf(request)
        if ticket_pdf:
            response = HttpResponse(ticket_pdf, content_type='application/pdf')
            filename = "Ticket_%s.pdf" % ("Try")
            content = "inline; filename='%s'" % (filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" % (filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")
        return HttpResponse(ticket_pdf, content_type='application/pdf')


def send_mail_with_pdf(request):
    content = get_template('customizations/send_mail.html').render()
    content = mark_safe(content)
    email = EmailMessage(
        'Test Send Ticket',
        content,
        'edacticket@gmail.com',
        ['test@gmail.com']
    )
    email.content_subtype = 'html'
    mime_type = mimetypes.guess_type('ticket_pdf.pdf')
    email.attach('ticket_pdf', generate_pdf(request), mime_type[0])
    email.send()
    return HttpResponseRedirect(r('customizations:successfully_mail'))


class ViewCreateCustomization(LoginRequiredMixin, FormView):
    form_class = FormCreateCustomization
    template_name = 'customizations/create.html'
    success_url = 'create.html'

    def post(self, request, *args, **kwargs):
        is_form_valid = super(ViewCreateCustomization, self).post(request, *args, **kwargs)
        if is_form_valid:
            select_event = request.POST.get('select_event')
            logo = request.POST.get('logo')
            message = request.POST.get('message')
            select_ticket_template = request.POST.get('select_ticket_template')
            ticket = TicketTemplate.objects.create()
            email = EmailConfirmation.objects.create(
                message=message,
                logo=logo
            )
            Customization.objects.create(
                user=self.request.user,
                ticket_template=ticket,
                email_confirmation=email

            )
            return HttpResponseRedirect('/')
