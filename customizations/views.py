# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, DeleteView
from django.conf import settings
from customizations.models import Customization, TicketTemplate, CustomEmail
from customizations.forms import FormCustomization
from django.core.files.storage import FileSystemStorage
import requests
import json
from pprint import pprint

class CustomizationConfig(LoginRequiredMixin):
    model = Customization
    form_class = FormCustomization
    success_url = reverse_lazy('/')


def create_webhook(token):
    response = requests.post(
        "https://www.eventbriteapi.com/v3/webhooks/",
        headers={
            "Authorization": 'Bearer ' + str(token),
        },
        data={
            "endpoint_url": "https://custom-ticket-heroku.herokuapp.com/mail/mail/",
            "actions": "order.placed",
            # "event_id": "all_events",
        },
        # Verify SSL certificate
        verify=True
    )
    pprint(response.json())
    return (response.json()[u'id'])


def get_token(request):
    token = request.user.social_auth.get(provider='eventbrite').access_token
    return token


class ViewCreateCustomization(LoginRequiredMixin, FormView):
    form_class = FormCustomization
    template_name = 'customizations/create.html'
    success_url = 'create.html'

    def post(self, request, *args, **kwargs):
        is_form_valid = super(ViewCreateCustomization, self).post(request, *args, **kwargs)
        if is_form_valid:
            name = request.POST.get('name')
            # logo = request.POST.get('logo')

            # image uploaded
            myfile = request.FILES['logo']
            fs = FileSystemStorage()
            domain = request.build_absolute_uri('/')[:-1]
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename)
            logo = domain + settings.MEDIA_URL + filename

            message = request.POST.get('message')
            select_design_template = request.POST.get('select_design_template')
            message_ticket = request.POST.get('message_ticket')
            token = get_token(request)
            webhook_id = create_webhook(token)
            ticket = TicketTemplate.objects.create(
                select_design_template=select_design_template,
                message_ticket=message_ticket
            )
            custom_email = CustomEmail.objects.create(
                message=message,
                logo=logo
            )
            Customization.objects.create(
                user=self.request.user,
                ticket_template=ticket,
                custom_email=custom_email,
                name=name,
                webhook_id=webhook_id,
            )
            return HttpResponseRedirect('/')


def update_customization(request, pk):
    user = request.user
    customization = get_object_or_404(Customization, pk=pk)
    form = FormCustomization(initial={
        'name': customization.name,
        'logo': customization.custom_email.logo,
        'message': customization.custom_email.message,
        'select_design_template': customization.ticket_template.select_design_template,
        'message_ticket': customization.ticket_template.message_ticket,

    })
    if request.method == 'POST':
        # form = FormCustomization(data=request.POST)
        form = FormCustomization(request.POST, request.FILES)
        if form.is_valid():
            customization.name = form.cleaned_data['name']
            customization.custom_email.logo = form.cleaned_data['logo']
            customization.custom_email.message = form.cleaned_data['message']
            customization.ticket_template.select_design_template = form.cleaned_data['select_design_template']
            customization.ticket_template.message_ticket = form.cleaned_data['message_ticket']
            customization.save()
            user.save()
            return redirect('/')

    context = {'form': form, 'instance': customization}
    return render(request, 'customizations/update.html', context)


class DeleteCustomization(CustomizationConfig, DeleteView):
    template_name = 'customizations/delete.html'
    success_url = reverse_lazy('home')
    context_object_name = 'customizations'

    def get_context_data(self, **kwargs):
        context = super(DeleteCustomization, self).get_context_data(**kwargs)
        context['user'] = self.get_object().user
        return context
