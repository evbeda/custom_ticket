# coding: utf-8
import StringIO

from django.core.mail import EmailMessage
from django.template import Context
from django.template.loader import get_template, render_to_string
from django.utils.safestring import mark_safe
from xhtml2pdf import pisa
from xhtml2pdf.pdf import pisaPDF


# class SendEmail(object):

#     def __init__(self, title, context, template, users):
#         self.title = title
#         self.context = context
#         self.template = template
#         self.users = users

#     def get_content(self):
#         content = get_template(self.template).render(Context({'context': self.context}))
#         return mark_safe(content)

#     def send(self):
#         email = EmailMessage(self.title, self.get_content(), 'edacticket@email.com', to=self.users)
#         email.content_subtype = 'html'
#         email.send()

#     def run(self):
#         self.send()


class PDF(object):

    def __init__(self, template, dataset=[]):
        self.template = template
        self.dataset = dataset
        self.pdf_base = pisaPDF()

    def render(self):
        for di in self.dataset:
            page = render_to_string(self.template, di)
            self.create_page(page)
        return self.pdf_base

    def create_page(self, page):
        data = StringIO.StringIO(page.encode('utf-8'))
        temp = StringIO.StringIO()
        pdf = pisa.pisaDocument(data, temp)
        self.pdf_base.addDocument(pdf)
