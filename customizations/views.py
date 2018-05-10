# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import (
    render,
    get_object_or_404,
    redirect,
)
from django.urls import reverse_lazy
from django.views.generic import (
    FormView,
    DeleteView,
    ListView,
)
from customizations.forms import (
    FormCustomization,
    FormBaseTickets,
)
from customizations.mixins import GroupRequiredMixin
from customizations.models import (
    Customization,
    TicketTemplate,
    CustomEmail,
    UserWebhook,
    BaseTicketTemplate,
)
from customizations.utils import (
    upload_file,
    generate_base_ticket,
)
from customizations.utils import (
    create_webhook,
    get_token,
    delete_webhook,
    in_group,
)


class ViewListBaseTickets(GroupRequiredMixin, LoginRequiredMixin, ListView):
    group_required = [u'admin']
    model = BaseTicketTemplate
    template_name = 'basetickets/home.html'

    def get_context_data(self, **kwargs):
        context = super(ViewListBaseTickets, self).get_context_data(**kwargs)
        context['basetickets'] = BaseTicketTemplate.objects.all()
        return context

    def get_queryset(self):
        return BaseTicketTemplate.objects.all()


class DeleteBaseTickets(GroupRequiredMixin, LoginRequiredMixin, DeleteView):
    model = BaseTicketTemplate
    group_required = [u'admin']
    template_name = 'basetickets/delete.html'
    success_url = '/customizations/home-baseticket'

    def get_context_data(self, **kwargs):
        context = super(DeleteBaseTickets, self).get_context_data(**kwargs)
        return context


class ViewCreateBaseTickets(GroupRequiredMixin, LoginRequiredMixin, FormView):
    form_class = FormBaseTickets
    group_required = [u'admin']
    template_name = 'basetickets/create.html'

    def post(self, request, *args, **kwargs):
        is_form_valid = super(ViewCreateBaseTickets, self).post(
            request, *args, **kwargs)
        links = upload_file(request, 'preview')
        if is_form_valid and bool(links):
            name = request.POST.get('name')
            template_source = request.POST.get('template_source')
            content_html = request.POST.get('content_html')
            BaseTicketTemplate.objects.create(
                name=name,
                template_source=template_source,
                preview=links['dropbox'],
                content_html=content_html
            )
            return HttpResponseRedirect('/customizations/home-baseticket')
        else:
            form = FormBaseTickets()

            return render(request, self.template_name, {
                'form': form}
            )


class ViewGenerateBaseTickets(GroupRequiredMixin, LoginRequiredMixin, FormView):
    form_class = FormBaseTickets
    group_required = [u'admin']
    template_name = 'basetickets/generate.html'

    def post(self, request, *args, **kwargs):
        is_form_valid = super(ViewGenerateBaseTickets, self).post(
            request, *args, **kwargs)
        if is_form_valid and BaseTicketTemplate.objects.count() == 0:
            generate_base_ticket(self)
            return HttpResponseRedirect('/customizations/home-baseticket')
        else:
            form = FormBaseTickets()
            form.error = 'You already have created base tickets.'
            return render(request, self.template_name, {
                'form': form}
            )


class CustomizationConfig(LoginRequiredMixin):
    model = Customization
    form_class = FormCustomization
    success_url = reverse_lazy('/')


class ListCustomizations(LoginRequiredMixin, ListView):
    model = Customization
    template_name = 'events/home.html'
    group = 'admin'

    def get_context_data(self, **kwargs):
        context = super(ListCustomizations, self).get_context_data(**kwargs)
        context['customizations'] = Customization.objects.filter(user=self.request.user)
        context['is_admin'] = in_group(self.group, self.request.user)
        return context

    def get_queryset(self):
        return Customization.objects.filter(user=self.request.user)


class ViewCreateCustomization(LoginRequiredMixin, FormView):
    form_class = FormCustomization
    template_name = 'customizations/create.html'
    success_url = 'create.html'

    def post(self, request, *args, **kwargs):
        form = FormCustomization(request.POST)
        links = upload_file(request, 'logo')
        partner_links = upload_file(request, 'image_partner')
        if Customization.objects.filter(user=request.user).exists():
            return HttpResponseRedirect('/customizations/error-create')
        else:
            # if we keep links['status'] the logo is a required field
            if form.is_valid():
                name = request.POST.get('name')
                message = request.POST.get('message')
                select_design_template = request.POST.get('select_design_template')
                message_ticket = request.POST.get('message_ticket')
                show_event_sequence = request.POST.get('show_event_sequence') == 'on'
                show_ticket_type_sequence = request.POST.get('show_ticket_type_sequence') == 'on'
                hide_ticket_type_price = request.POST.get('hide_ticket_type_price') == 'on'
                footer_description = request.POST.get('footer_description')
                double_ticket = request.POST.get('double_ticket') == 'on'
                pdf_ticket_attach = request.POST.get('pdf_ticket_attach')
                template = get_object_or_404(
                    BaseTicketTemplate,
                    pk=select_design_template)
                ticket = TicketTemplate.objects.create(
                    select_design_template=template,
                    message_ticket=message_ticket,
                    show_event_sequence=show_event_sequence,
                    show_ticket_type_sequence=show_ticket_type_sequence,
                    hide_ticket_type_price=hide_ticket_type_price,
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
                return render(request, self.template_name, {
                    'form': form}
                )


def update_customization(request, pk):

    customization = get_object_or_404(Customization, pk=pk)
    custom_email = get_object_or_404(CustomEmail, pk=pk)
    ticket_template = get_object_or_404(TicketTemplate, pk=pk)

    form = FormCustomization(initial={
        'name': customization.name,
        'logo': custom_email.logo,
        'message': custom_email.message,
        'select_design_template': ticket_template.select_design_template_id,
        'message_ticket': ticket_template.message_ticket,
        'footer_description': ticket_template.footer_description,
        'show_event_sequence': ticket_template.show_event_sequence,
        'show_ticket_type_sequence': ticket_template.show_ticket_type_sequence,
        'hide_ticket_type_price': ticket_template.hide_ticket_type_price,
        'double_ticket': ticket_template.double_ticket,
        'image_partner': custom_email.image_partner,
        'pdf_ticket_attach': customization.pdf_ticket_attach,
    })
    if request.method == 'POST':
        # form = FormCustomization(data=request.POST)
        form = FormCustomization(request.POST, request.FILES)
        if form.is_valid():
            customization.name = form.cleaned_data['name']
            if form.cleaned_data['logo'] is not None:
                links = upload_file(request, 'logo')
                custom_email.logo = links['dropbox'],
                custom_email.logo_local = links['local'],
                custom_email.logo_path = links['path'],
                custom_email.logo_name = links['name'],
                custom_email.logo_url = links['dropbox'],
            customization.pdf_ticket_attach = form.cleaned_data['pdf_ticket_attach']
            custom_email.message = form.cleaned_data['message']
            if form.cleaned_data['image_partner'] is not None:
                partner_links = upload_file(request, 'image_partner')
                custom_email.image_partner = partner_links['dropbox'],
                custom_email.image_partner_local = partner_links['local'],
                custom_email.image_partner_path = partner_links['path'],
                custom_email.image_partner_name = partner_links['name'],

            ticket_template.select_design_template = get_object_or_404(
                BaseTicketTemplate,
                pk=form.cleaned_data['select_design_template']
            )
            ticket_template.message_ticket = form.cleaned_data[
                'message_ticket']
            ticket_template.footer_description = form.cleaned_data[
                'footer_description']
            ticket_template.show_event_sequence = form.cleaned_data[
                'show_event_sequence']
            ticket_template.show_ticket_type_sequence = form.cleaned_data[
                'show_ticket_type_sequence']
            ticket_template.hide_ticket_type_price = form.cleaned_data[
                'hide_ticket_type_price']
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
    success_url = reverse_lazy('list_customizations')
    context_object_name = 'customizations'

    def get_context_data(self, **kwargs):
        if Customization.objects.filter(user=self.request.user).count() == 1:
            webhook_id = UserWebhook.objects.get(user=self.request.user).webhook_id
            token = get_token(self.request.user)
            delete_webhook(token, webhook_id)
        context = super(DeleteCustomization, self).get_context_data(**kwargs)
        context['user'] = self.get_object().user

        return context
