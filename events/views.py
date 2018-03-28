# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from events.models import Customization
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from eventbrite import Eventbrite


class EventsView(LoginRequiredMixin, TemplateView):
    template_name = "events/events.html"

    def get_context_data(self, **kwargs):
        context = super(EventsView, self).get_context_data(**kwargs)
        '''access_token = self.request.user.social_auth.get(
        provider='eventbrite'
        ).access_token'''
        '''
        If we have more than 2 users,
        we need to use the filter.
        But the filter does not work with -.access_token-
        '''
        access_token = self.request.user.social_auth.all()[0].access_token
        eventbrite = Eventbrite(access_token)
        context['events'] = [
            event
            # Status : live, draft, canceled, started, ended, all
            for event in eventbrite.get(
                '/users/me/events/?status=live,draft'
            )['events']
        ]
        return context


class HomeView(LoginRequiredMixin, ListView):
    model = Customization
    template_name = 'events/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        return context

    #Get ticket_classes, example:

    # import request
    # url = "https://www.eventbriteapi.com/v3/users/owned_events/?token=" + str(access_token)
    # "https://www.eventbriteapi.com/v3/events/" + eventID + "/ticket_classes/?token=" + access_token
    # response = requests.get(url)
    # print response.json()['events'][0]['name']['text']

    # def get_event_ticket_classes(self, id, **data):
    #     """
    #     GET /events/:id/ticket_classes/
    #     Returns a paginated response with a key of ``ticket_classes``,
    #     containing a list of :format:`ticket_class`.
    #     """
    #     return self.get("/events/{0}/ticket_classes/".format(id), data=data)
