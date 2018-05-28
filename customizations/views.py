# -*- coding: utf-8 -*-

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import (
    render,
    get_object_or_404,
    redirect,
)
from django.template import loader
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
    DTOCustomization,
)
from customizations.utils import (
    delete_webhook,
    generate_base_ticket,
    get_token,
    in_group,
    upload_file,
)
from services import (
    compose_customization,
    edit_customization,
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


def update_base_tickets(request, pk):
    base = get_object_or_404(BaseTicketTemplate, pk=pk)
    form = FormBaseTickets(initial={
        'template_source': base.template_source,
        'name': base.name,
        'preview': base.preview,
        'content_html': base.content_html,
        'aspect_ratio_logo_x': base.aspect_ratio_logo_x,
        'aspect_ratio_logo_y': base.aspect_ratio_logo_y,
        'aspect_ratio_image_x': base.aspect_ratio_image_x,
        'aspect_ratio_image_y': base.aspect_ratio_image_y,
    })
    if request.method == 'POST':
        form = FormBaseTickets(request.POST, request.FILES)
        if form.is_valid():
            base.template_source = form.cleaned_data['template_source']
            base.name = form.cleaned_data['name']
            if form.cleaned_data['preview'] is not None:
                base.preview = form.cleaned_data['preview']
            base.content_html = form.cleaned_data['content_html']
            base.aspect_ratio_logo_x = form.cleaned_data['aspect_ratio_logo_x']
            base.aspect_ratio_logo_y = form.cleaned_data['aspect_ratio_logo_y']
            base.aspect_ratio_image_x = form.cleaned_data['aspect_ratio_image_x']
            base.aspect_ratio_image_y = form.cleaned_data['aspect_ratio_image_y']
            base.save()

            return HttpResponseRedirect('/customizations/home-baseticket')
        else:
            context = {
                'form': form,
                'instance': base
            }
            return render(request, 'basetickets/create.html', context)

    context = {
        'form': form,
        'instance': base
    }
    return render(request, 'basetickets/create.html', context)


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

            return render(
                request,
                self.template_name,
                {
                    'form': form,
                }
            )


class ViewGenerateBaseTickets(
    GroupRequiredMixin,
    LoginRequiredMixin,
    FormView
):
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
            return render(
                request,
                self.template_name,
                {
                    'form': form,
                }
            )


class CustomizationConfig(LoginRequiredMixin):
    model = Customization
    form_class = FormCustomization
    success_url = reverse_lazy('/')


class ListCustomizations(LoginRequiredMixin, ListView):
    model = Customization
    template_name = 'customizations/list.html'
    group = 'admin'

    def get_context_data(self, **kwargs):
        context = super(ListCustomizations, self).get_context_data(**kwargs)
        context['customizations'] = Customization.objects.filter(
            user=self.request.user
        )
        context['is_admin'] = in_group(self.group, self.request.user)
        return context

    def get_queryset(self):
        return Customization.objects.filter(user=self.request.user)


class ViewCreateCustomization(LoginRequiredMixin, FormView):
    form_class = FormCustomization
    template_name = 'customizations/create.html'
    success_url = 'create.html'

    def get_context_data(self, **kwargs):
        context = super(
            ViewCreateCustomization, self
        ).get_context_data(**kwargs)
        modal_template = loader.get_template('includes/modal_crop_image.html')
        context['modal_crop_image'] = modal_template.render()
        return context

    def post(self, request, *args, **kwargs):
        form = FormCustomization(request.POST)
        modal_template = loader.get_template('includes/modal_crop_image.html')
        modal_crop_image = modal_template.render()
        if Customization.objects.filter(user=request.user).exists():
            return HttpResponseRedirect('/customizations/error-create')
        else:
            if form.is_valid():
                dto_customization = DTOCustomization(**form.cleaned_data)
                links_logo = upload_file(request, 'logo')
                customization = compose_customization(
                    dto=dto_customization,
                    user=request.user,
                    links_logo=links_logo,
                    url_request=request.build_absolute_uri('/')[:-1]
                )
                if customization['status']:
                    return HttpResponseRedirect('/')
                else:
                    print customization['error']
                    form.error = 'An unexpected error has occurred. ' \
                                 'Please try again.'
                    return render(
                        request,
                        self.template_name,
                        {
                            'form': form,
                            'modal_crop_image': modal_crop_image,
                        }
                    )
            else:
                form.error = 'The form is not valid. Please check that ' \
                             'you have completed the required ' \
                             'fields correctly.'
                return render(
                    request,
                    self.template_name,
                    {
                        'form': form,
                        'modal_crop_image': modal_crop_image,
                    }
                )


def update_customization(request, pk):
    modal_template = loader.get_template('includes/modal_crop_image.html')
    modal_crop_image = modal_template.render()
    customization = get_object_or_404(Customization, pk=pk)
    custom_email = get_object_or_404(
        CustomEmail,
        pk=customization.custom_email.id
    )
    ticket_template = get_object_or_404(
        TicketTemplate,
        pk=customization.ticket_template.id
    )

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
        form = FormCustomization(request.POST, request.FILES)
        if form.is_valid():
            links_logo = upload_file(request, 'logo')
            dto_customization = DTOCustomization(
                customization=customization,
                custom_email=custom_email,
                ticket_template=ticket_template,
                **form.cleaned_data
            )
            if edit_customization(
                dto=dto_customization,
                links_logo=links_logo,
                user=request.user,
            ):
                return redirect('/')
            else:
                context = {
                    'form': form,
                    'instance': customization,
                    'modal_crop_image': modal_crop_image,
                }
                return render(request, 'customizations/create.html', context)

    context = {
        'form': form,
        'instance': customization,
        'modal_crop_image': modal_crop_image,
    }
    return render(request, 'customizations/create.html', context)


class DeleteCustomization(CustomizationConfig, DeleteView):
    template_name = 'customizations/delete.html'
    success_url = reverse_lazy('list_customizations')
    context_object_name = 'customizations'

    def post(self, request, *args, **kwargs):
        if self.request.method == 'POST':
            pk = self.kwargs['pk']
            user = self.request.user
            delete_customizations(pk, user)
            return redirect('/')

    def get_context_data(self, **kwargs):
        context = super(DeleteCustomization, self).get_context_data(**kwargs)
        context['user'] = self.get_object().user

        return context


def delete_customizations(pk, user):
    if Customization.objects.filter(user=user).exists():
        webhook_id = UserWebhook.objects.get(user=user).webhook_id
        token = get_token(user)
        delete_webhook(token, webhook_id)
    customization = Customization.objects.get(id=pk)
    custom_email = CustomEmail.objects.get(
        id=customization.custom_email.id,
    )
    ticket_template = TicketTemplate.objects.get(
        id=customization.ticket_template.id,
    )
    customization.delete()
    custom_email.delete()
    ticket_template.delete()
