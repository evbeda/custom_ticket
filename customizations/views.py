# -*- coding: utf-8 -*-
import datetime
# import mimetypes
from core.utils import render_to_pdf
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse as r
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from django.views.generic import View


class GeneratePdf(View):
    def get(self, request, *args, **kwargs):
        data = {
            'today': datetime.date.today(),
            'type': 'VIP',
            'customer_name': 'Name ABC',
            'order_id': 1233434,
        }
        ticket_pdf = render_to_pdf('tickets/template_default.html', data)
        if ticket_pdf:
            response = HttpResponse(ticket_pdf, content_type='application/pdf')
            filename = "Ticket_%s.pdf" % ("Try")
            content = "inline; filename='%s'" % (filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" % (filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")
        return HttpResponse(ticket_pdf, content_type='application/pdf')


def send_mail_with_pdf(request):

    content = get_template('customizations/send_mail.html').render()
    content = mark_safe(content)
    email = EmailMessage('Test Send Ticket', content, 'edacticket@gmail.com', ['test@gmail.com'])
    email.content_subtype = 'html'
    '''
    attach email --progress
    '''
    # mime_type = mimetypes.guess_type('ticket_pdf.pdf')
    # email.attach('ticket-pdf', (request), mime_type[0])
    email.send()
    return HttpResponseRedirect(r('customizations:successfully_mail'))
