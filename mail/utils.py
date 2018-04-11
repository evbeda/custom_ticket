# coding: utf-8
import StringIO

from django.template.loader import render_to_string
from xhtml2pdf import pisa
from xhtml2pdf.pdf import pisaPDF


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
