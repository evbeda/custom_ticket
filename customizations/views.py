# -*- coding: utf-8 -*-
from core.utils import PDF
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse as r
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView, DeleteView
from events.models import Customization, TicketTemplate, CustomEmail, TicketType
from .forms import FormCustomization, FormSendEmailPreview


def get_pdf_ticket(self):
    data = TicketType.data_to_dict(1)
    return PDF('tickets/template_default.html', [data]).render().getvalue()



def generate_pdf_ticket(request):
    ticket_pdf = get_pdf_ticket(request)
    return HttpResponse(ticket_pdf, content_type='application/pdf')


def get_pdf_body_email(request):
    data = CustomEmail.data_to_dict(1)
    return PDF('customizations/body_mail.html', [data]).render().getvalue()


def email_preview_pdf(request):
    email_pdf = get_pdf_body_email(request)
    return HttpResponse(email_pdf, content_type='application/pdf')

# not use for testing - use do_send_email in mail/views.py
def send_mail_with_ticket_pdf(request):
    data = CustomEmail.data_to_dict(1)
    content = render_to_string('customizations/body_mail.html', context=data)
    content = mark_safe(content)
    email = EmailMessage(
        'Test Send Ticket',
        content,
        'edacticket@gmail.com',
        ['usercticket@gmail.com']
    )
    email.content_subtype = 'html'
    pdf = get_pdf_ticket(request)
    email.attach('ticket', pdf, 'application/pdf')
    email.send()
    return HttpResponseRedirect(r('customizations:successfully_mail'))

# not use for testing - use do_send_email in mail/views.py
def send_mail_test(request):
    data = CustomEmail.data_to_dict(1)
    content = render_to_string('customizations/body_mail.html', context=data)
    content = mark_safe(content)
    email = GetEmailTest()
    email = EmailMessage(
        'Test Send Ticket',
        content,
        'edacticket@gmail.com',
        ['usercticket@gmail.com']
    )
    email.content_subtype = 'html'
    pdf = get_pdf_ticket(request)
    email.attach('ticket', pdf, 'application/pdf')
    email.send()
    return HttpResponseRedirect(r('customizations:successfully_mail'))


class CustomizationConfig(LoginRequiredMixin):
    model = Customization
    form_class = FormCustomization
    success_url = reverse_lazy('/')


class ListCustomization(CustomizationConfig, ListView):
    template_name = "list.html"
    context_object_name = "customizations"

    def get_queryset(self):
        return Customization.objects.all()


class ViewCreateCustomization(LoginRequiredMixin, FormView):
    form_class = FormCustomization
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
            email = CustomEmail.objects.create(
                message=message,
                logo=logo
            )
            Customization.objects.create(
                user=self.request.user,
                ticket_template=ticket,
                custom_email=email

            )
            return HttpResponseRedirect('/')


# class UpdateCustomization(CustomizationConfig, UpdateView):
#     template_name = 'customizations/update.html'
#     success_url = reverse_lazy('customizations:list')
#     context_object_name = 'customizations'

#     def get_context_data(self, **kwargs):
#         context = super(UpdateCustomization, self).get_context_data(**kwargs)
#         context['customization'] = self.get_object()
#         return context

#     def post(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         customization = self.get_object()
#         form = FormCustomization(self.request.POST, instance=customization)
#         if form.is_valid():
#             form.save()
#             messages.info(request, u'Update ok!')
#             return HttpResponseRedirect(r('customizations:list'))
#         else:
#             return render(request, 'customizations:update_customization', {'form': form})


class DeleteCustomization(CustomizationConfig, DeleteView):
    template_name = 'customizations/delete.html'
    success_url = reverse_lazy('home')
    context_object_name = 'customizations'

    def get_context_data(self, **kwargs):
        context = super(DeleteCustomization, self).get_context_data(**kwargs)
        context['user'] = self.get_object().user
        return context


class GetEmailTest(LoginRequiredMixin, FormView):
    form_class = FormSendEmailPreview
    template_name = 'customizations/form_mail.html'
    success_url = 'form_mail.html'

    def post_email(self, request, *args, **kwargs):
        is_form_valid = super(GetEmailTest, self).post(request, *args, **kwargs)
        if is_form_valid:
            email_send = request.POST.get('email_send')
            return email_send

    # def get_data_ticket(request):
    #     if request.method == 'GET':
    #         form = FormCustomization(request.GET)
    #         if form.is_valid():
    #             logo = form.cleaned_data['logo']
    #             message = form.cleaned_data['message']
    #     else:
    #         form = FormCustomization()

    #     context = {
    #         'logo': logo,
    #         'message': message
    #     }
    #     return render(request, 'customizations:form_mail', context)
