# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from eventbrite import Eventbrite


class EventsView(LoginRequiredMixin, TemplateView):

    template_name = "events/events.html"

    def get_context_data(self, **kwargs):
        context = super(EventsView, self).get_context_data(**kwargs)
        access_token = self.request.user.social_auth.get(provider='eventbrite').access_token
        eventbrite = Eventbrite(access_token)
        context['events'] = [
            event
            # Status : live, draft, canceled, started, ended, all
            for event in eventbrite.get('/users/me/events/?status=live,draft')['events']
        ]
        return context


class TicketsView(LoginRequiredMixin, TemplateView):
    template_name = "events/show_tickets.html"
