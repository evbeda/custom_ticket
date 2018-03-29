# -*- coding: utf-8 -*-
import datetime
from core.utils import PDF
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse as r
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, render_to_response
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from django.views.generic import View, FormView
from events.models import Customization, TicketTemplate, EmailConfirmation
from .forms import FormCreateCustomization, FormSendEmailPreview


def get_pdf(request):
    data = {
        'today': datetime.date.today(),
        'type': 'VIP',
        'customer_name': 'Name ABC',
        'order_id': 1233434,
    }
    return PDF('tickets/template_default.html', [data]).render().getvalue()


def generate_pdf(request):
    ticket_pdf = get_pdf(request)
    return HttpResponse(ticket_pdf, content_type='application/pdf')


def email_preview(request):
    data = {
        'today': datetime.date.today(),
        'type': 'VIP',
        'customer_name': 'Name ABC',
        'order_id': 1233434,
    }
    ticket_pdf = PDF('customizations/send_mail.html', [data]).render()
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


# class CreateBodyEmail(LoginRequiredMixin, ListView):
#     model = Customization
#     template_name = 'customizations/send_mail.html'

#     def get_context_data(self, **kwargs):
#         context = super(ListView, self).get_context_data(**kwargs)
#         return render_to_response(context, **kwargs)


def send_mail_with_pdf(request):
    # content = CreateBodyEmail()
    content = get_template('customizations/send_mail.html').render()
    content = mark_safe(content)
    email = EmailMessage(
        'Test Send Ticket',
        content,
        'edacticket@gmail.com',
        ['usercticket@gmail.com']
    )
    email.content_subtype = 'html'
    pdf = get_pdf(request)
    email.attach('ticket', pdf, 'application/pdf')
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


class ViewSendPreview(LoginRequiredMixin, FormView):
    form_class = FormSendEmailPreview
    template_name = 'customizations/form_mail.html'
    success_url = 'form_mail.html'

    def post(self, request, *args, **kwargs):
        is_form_valid = super(ViewSendPreview, self).post(request, *args, **kwargs)
        if is_form_valid:
            email_send = request.POST.get('email_send')
            return HttpResponseRedirect('/')
