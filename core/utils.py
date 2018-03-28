# coding: utf-8
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from django.utils.safestring import mark_safe

from io import BytesIO
from xhtml2pdf import pisa


class SendEmail(object):

    def __init__(self, title, context, template, users):
        self.title = title
        self.context = context
        self.template = template
        self.users = users

    def get_content(self):
        content = get_template(self.template).render(Context({'context': self.context}))
        return mark_safe(content)

    def send(self):
        email = EmailMessage(self.title, self.get_content(), 'email@email.com', to=self.users)
        email.content_subtype = 'html'
        email.send()

    def run(self):
        self.send()


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None
