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
from customizations.utils import upload_file
from customizations.utils import create_webhook, get_token, delete_webhook
from customizations.utils import (
    upload_file,
    create_webhook,
    get_token,
    delete_webhook
)


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
        links = upload_file(request, 'logo')

        if is_form_valid and bool(links):
            name = request.POST.get('name')
            links = upload_file(request, 'logo')
            partner_links = upload_file(request, 'image_partner')
            message = request.POST.get('message')
            select_design_template = request.POST.get('select_design_template')
            message_ticket = request.POST.get('message_ticket')
            show_event_sequence = request.POST.get('show_event_sequence') == 'on'
            show_ticket_type_sequence = request.POST.get('show_ticket_type_sequence') == 'on'
            show_ticket_type_price = request.POST.get('show_ticket_type_price') == 'on'
            footer_description = request.POST.get('footer_description')
            double_ticket = request.POST.get('double_ticket') == 'on'

            pdf_ticket_attach = request.POST.get('pdf_ticket_attach')

            ticket = TicketTemplate.objects.create(
                select_design_template=select_design_template,
                message_ticket=message_ticket,
                show_event_sequence=show_event_sequence,
                show_ticket_type_sequence=show_ticket_type_sequence,
                show_ticket_type_price=show_ticket_type_price,
                footer_description=footer_description,
                double_ticket=double_ticket,
            )
            custom_email = CustomEmail.objects.create(
                message=message,
                logo=links['dropbox'],
                logo_local=links['local'],
                logo_path=links['path'],
                logo_name=links['name'],
                logo_url=links['dropbox'],

                image_partner=partner_links['dropbox'],
                image_partner_local=partner_links['local'],
                image_partner_path=partner_links['path'],
                image_partner_name=partner_links['name'],
                image_partner_url=partner_links['dropbox'],
            )
            Customization.objects.create(
                user=self.request.user,
                ticket_template=ticket,
                custom_email=custom_email,
                name=name,
                pdf_ticket_attach=pdf_ticket_attach,
            )
            if not UserWebhook.objects.filter(user=request.user).exists():
                token = get_token(request.user)
                webhook_id = create_webhook(token)
                UserWebhook.objects.create(
                    user=self.request.user,
                    webhook_id=webhook_id,
                )
            return HttpResponseRedirect('/')
        else:
            form = FormCustomization()
            return render(request, self.template_name, {
                'form': form}
            )


def update_customization(request, pk):

    customization = get_object_or_404(Customization, pk=pk)
    custom_email = get_object_or_404(CustomEmail, pk=pk)
    ticket_template = get_object_or_404(TicketTemplate, pk=pk)

    form = FormCustomization(initial={
        'name': customization.name,
        'pdf_ticket_attach': customization.pdf_ticket_attach,
        'logo': custom_email.logo,
        'message': custom_email.message,
        'image_partner': custom_email.image_partner,
        'select_design_template': ticket_template.select_design_template,
        'message_ticket': ticket_template.message_ticket,
        'footer_description': ticket_template.footer_description,
        'show_event_sequence': ticket_template.show_event_sequence,
        'show_ticket_type_sequence': ticket_template.show_ticket_type_sequence,
        'show_ticket_type_price': ticket_template.show_ticket_type_price,
        'double_ticket': ticket_template.double_ticket,

    })
    if request.method == 'POST':
        # form = FormCustomization(data=request.POST)
        form = FormCustomization(request.POST, request.FILES)
        if form.is_valid():
            customization.name = form.cleaned_data['name']
            customization.pdf_ticket_attach = form.cleaned_data['pdf_ticket_attach']
            custom_email.logo = form.cleaned_data['logo']
            custom_email.message = form.cleaned_data['message']
            custom_email.image_partner = form.cleaned_data['image_partner']
            ticket_template.select_design_template = form.cleaned_data[
                'select_design_template']
            ticket_template.message_ticket = form.cleaned_data[
                'message_ticket']
            ticket_template.footer_description = form.cleaned_data[
                'footer_description']
            ticket_template.show_event_sequence = form.cleaned_data[
                'show_event_sequence']
            ticket_template.show_ticket_type_sequence = form.cleaned_data[
                'show_ticket_type_sequence']
            ticket_template.show_ticket_type_price = form.cleaned_data[
                'show_ticket_type_price']
            ticket_template.double_ticket = form.cleaned_data[
                'double_ticket']
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
        if Customization.objects.filter(user=self.request.user).count() == 1:
            webhook_id = UserWebhook.objects.get(user=self.request.user).webhook_id
            token = get_token(self.request.user)
            delete_webhook(token, webhook_id)
        context = super(DeleteCustomization, self).get_context_data(**kwargs)
        context['user'] = self.get_object().user

        return context
