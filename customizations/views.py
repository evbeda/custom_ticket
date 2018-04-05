# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse as r
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.urls import reverse_lazy
from django.views.generic import FormView, DeleteView
from events.models import Customization, TicketTemplate, CustomEmail
from .forms import FormCustomization, FormSendEmailPreview


class CustomizationConfig(LoginRequiredMixin):
    model = Customization
    form_class = FormCustomization
    success_url = reverse_lazy('/')


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
