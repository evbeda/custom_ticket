# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, DeleteView
from customizations.models import (
    Customization,
    TicketTemplate,
    CustomEmail,
    UserWebhook
)
from customizations.forms import FormCustomization
from customizations.utils import upload_file,file_exist,download
from customizations.utils import create_webhook, get_token, delete_webhook


class CustomizationConfig(LoginRequiredMixin):
    model = Customization
    form_class = FormCustomization
    success_url = reverse_lazy('/')


class ViewCreateCustomization(LoginRequiredMixin, FormView):
    form_class = FormCustomization
    template_name = 'customizations/create.html'
    success_url = 'create.html'

    def post(self, request, *args, **kwargs):
        is_form_valid = super(ViewCreateCustomization, self).post(
            request, *args, **kwargs)
        if is_form_valid:
            name = request.POST.get('name')

            links = upload_file(request, 'logo')
            message = request.POST.get('message')
            select_design_template = request.POST.get('select_design_template')
            message_ticket = request.POST.get('message_ticket')

            ticket = TicketTemplate.objects.create(
                select_design_template=select_design_template,
                message_ticket=message_ticket
            )
            custom_email = CustomEmail.objects.create(
                message=message,
                logo=links['dropbox'],
                logo_local=links['local'],
                logo_path=links['path'],
                logo_name=links['name'],
                logo_url=links['dropbox']
            )
            Customization.objects.create(
                user=self.request.user,
                ticket_template=ticket,
                custom_email=custom_email,
                name=name,
            )
            if not UserWebhook.objects.filter(user=request.user).exists():
                token = get_token(request.user)
                webhook_id = create_webhook(token)
                UserWebhook.objects.create(
                    user=self.request.user,
                    webhook_id=webhook_id,
                )
            return HttpResponseRedirect('/')


def update_customization(request, pk):

    customization = get_object_or_404(Customization, pk=pk)
    custom_email = get_object_or_404(CustomEmail, pk=pk)
    ticket_template = get_object_or_404(TicketTemplate, pk=pk)

    form = FormCustomization(initial={
        'name': customization.name,
        'logo': custom_email.logo,
        'message': custom_email.message,
        'select_design_template': ticket_template.select_design_template,
        'message_ticket': ticket_template.message_ticket,

    })
    if request.method == 'POST':
        # form = FormCustomization(data=request.POST)
        form = FormCustomization(request.POST, request.FILES)
        if form.is_valid():
            customization.name = form.cleaned_data['name']
            custom_email.logo = form.cleaned_data['logo']
            custom_email.message = form.cleaned_data['message']
            ticket_template.select_design_template = form.cleaned_data[
                'select_design_template']
            ticket_template.message_ticket = form.cleaned_data['message_ticket']
            custom_email.save()
            ticket_template.save()
            customization.save()
            return redirect('/')

    context = {'form': form, 'instance': customization}
    return render(request, 'customizations/update.html', context)


class DeleteCustomization(CustomizationConfig, DeleteView):
    template_name = 'customizations/delete.html'
    success_url = reverse_lazy('home')
    context_object_name = 'customizations'

    def get_context_data(self, **kwargs):
        if Customization.objects.filter().count() == 1:
            webhook_id = UserWebhook.objects.filter(user=self.request.user)[0].webhook_id
            token = get_token(self.request.user)
            delete_webhook(token, webhook_id)
        context = super(DeleteCustomization, self).get_context_data(**kwargs)
        context['user'] = self.get_object().user

        return context
