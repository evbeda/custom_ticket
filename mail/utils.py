# coding: utf-8
import StringIO

from django.template.loader import render_to_string
from multiprocessing import Pool

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


def async(decorated):
    r'''Wraps a top-level function around an asynchronous dispatcher.

        when the decorated function is called, a task is submitted to a
        process pool, and a future object is returned, providing access to an
        eventual return value.

        The future object has a blocking get() method to access the task
        result: it will return immediately if the job is already done, or block
        until it completes.

        This decorator won't work on methods, due to limitations in Python's
        pickling machinery (in principle methods could be made pickleable, but
        good luck on that).
    '''
    # Keeps the original function visible from the module global namespace,
    # under a name consistent to its __name__ attribute. This is necessary for
    # the multiprocessing pickling machinery to work properly.

    def send(*args, **opts):
        return Pool().apply_async(decorated, args, opts)

    return send
