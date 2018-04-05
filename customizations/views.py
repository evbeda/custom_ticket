# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse as r
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView, DeleteView, UpdateView
from events.models import Customization, TicketTemplate, CustomEmail
from .forms import FormCustomization


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


class UpdateCustomization(CustomizationConfig, UpdateView):
    template_name = 'customizations/update.html'
    success_url = reverse_lazy('customizations:list')
    context_object_name = 'customizations'

    def get_context_data(self, **kwargs):
        context = super(UpdateCustomization, self).get_context_data(**kwargs)
        context['customization'] = self.get_object()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        customization = self.get_object()
        form = FormCustomization(self.request.POST, instance=customization)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(r('customizations:list'))
        else:
            return render(request, 'customizations:update_customization', {'form': form})


class DeleteCustomization(CustomizationConfig, DeleteView):
    template_name = 'customizations/delete.html'
    success_url = reverse_lazy('home')
    context_object_name = 'customizations'

    def get_context_data(self, **kwargs):
        context = super(DeleteCustomization, self).get_context_data(**kwargs)
        context['user'] = self.get_object().user
        return context
