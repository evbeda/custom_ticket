# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.mixins import LoginRequiredMixin

from django.http import (
    HttpResponse,
)
from django.shortcuts import (
    render,
    get_object_or_404,
)
from .tasks import get_data
from django.views.generic import FormView
from customizations.models import (
    Customization,
)
from mail.forms import FormSendEmailPreview
from mail.domain import (
    CustomData,
    data_fake,
)
from mail.tasks import do_send_email
from mail.utils import PDF


def get_pdf_ticket(request, pk):
    data = data_fake(pk)
    customization = get_object_or_404(Customization, pk=pk)
    html_url = customization.ticket_template.select_design_template.template_source
    pdf = PDF(html_url, [data]).render().getvalue()
    return HttpResponse(pdf, content_type='application/pdf')


def email_preview_pdf(request, pk):
    data = data_fake(pk)
    return render(request, 'mail/body_mail.html', context=data)


def accept_webhook(request):
    print 'Here! accepting webhook'
    get_data.delay(request.body, request.build_absolute_uri('/')[:-1])
    # threading.Thread(target=get_data, args=(request,)).start()
    print "responding webhook"
    return HttpResponse()


def get_url(attendee):
    url = attendee['url']
    return url


class GetEmailTest(LoginRequiredMixin, FormView):
    form_class = FormSendEmailPreview
    template_name = 'mail/form_mail.html'

    def form_valid(self, form):
        print form.cleaned_data
        # organizer_message = form.cleaned_data['organizer_message']
        # attendee_quantity = form.cleaned_data['attendee_quantity']
        # attendee_question = form.cleaned_data['attendee_question']
        # event_image = form.cleaned_data['event_image']

        attendees = []
        attendee = {
            'attendee_first_name': form.cleaned_data['attendee_first_name'],
            'attendee_last_name': form.cleaned_data['attendee_last_name'],
            'cost_gross': form.cleaned_data['attendee_cost_gross'],
            'barcode': form.cleaned_data['attendee_barcode'],
            'answers': {},
            'ticket_class': form.cleaned_data['ticket_class']
        }
        customization = Customization.objects.get(pk=self.kwargs['pk'])
        ticket_template = customization.ticket_template
        template_url = customization.ticket_template.select_design_template.template_source
        attendees.append(dict(attendee))
        custom_data = CustomData(
            domain=self.request.build_absolute_uri('/')[:-1],
            customization=customization,
            attendees=attendees,
            event_name_text=form.cleaned_data['event_name_text'],
            event_start=form.cleaned_data['event_start'],
            event_venue_location={form.cleaned_data['event_venue_location']},
            organizer_name=form.cleaned_data['organizer_name'],
            organizer_email={form.cleaned_data['organizer_email']},
            #   reserved seating
            user_order_email=form.cleaned_data['user_order_email'],
            order_id='1212',
            order_created=form.cleaned_data['order_created'],
            user_order_first_name=form.cleaned_data['user_order_first_name'],
            user_order_last_name=form.cleaned_data['user_order_last_name'],
            order_status=form.cleaned_data['order_status'],
            # payment_datetime='',
            from_email=form.cleaned_data['from_email'],
            emails=[form.cleaned_data['emails']],
            footer_description=ticket_template.footer_description,
            is_test=True,
            template_url=template_url,
        )
        return do_send_email(custom_data)
        # Fixme: double response.
        # return HttpResponseRedirect(reverse('mails:successfully_mail'))
