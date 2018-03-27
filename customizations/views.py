# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import FormView
from django.http import HttpResponse, HttpResponseRedirect
from forms import FormCreateCustomization
from django.contrib.auth.mixins import LoginRequiredMixin
from events.models import Customization,TicketTemplate, EmailConfirmation
from django.shortcuts import render

class ViewCreateCustomization(LoginRequiredMixin, FormView):
    form_class = FormCreateCustomization
    template_name = 'customizations/create.html'
    success_url = 'create.html'

    def post(self, request, *args, **kwargs):
        is_form_valid = super(ViewCreateCustomization, self).post(request,*args, **kwargs)

        if is_form_valid:
            select_event = request.POST.get('select_event')
            logo = request.POST.get('logo')
            message = request.POST.get('message')
            select_ticket_template = request.POST.get('select_ticket_template')

            ticket = TicketTemplate.objects.create()
            email = EmailConfirmation.objects.create(
                message=message,
            )
            Customization.objects.create(
                user=self.request.user,
                ticket_template=ticket,
                email_confirmation=email

            )
            return HttpResponseRedirect('/customizations/')
