# Custom ticket Django App
[![Coverage Status](https://coveralls.io/repos/github/evbeda/custom_ticket/badge.svg?branch=master)](https://coveralls.io/github/evbeda/custom_ticket?branch=master)
[![Build Status](https://travis-ci.org/evbeda/custom_ticket.svg?branch=master)](https://travis-ci.org/evbeda/custom_ticket)

As an organizer I want to be able to set a default template for both email and pdf ticket that will be automatically applied to any event created on my account.

# Getting Started

We assume that you have already created and activated a virtual environment

> clone

```python
$ git clone https://github.com/evbeda/custom_ticket.git

```

> install requeriments

```python
(env) $ pip install -r requeriments.txt

```

> set environment
```python
(env) $ export EMAIL_HOST=your_host
(env) $ export EMAIL_PORT=int
(env) $ export EMAIL_HOST_USER=user
(env) $ export EMAIL_HOST_PASSWORD=pass
(env) $ export EMAIL_USE_TLS=bool
(env) $ export SOCIAL_AUTH_EVENTBRITE_SECRET=secret
(env) $ export SOCIAL_AUTH_EVENTBRITE_KEY=key
(env) $ export DEBUG=bool
(env) $ export SERVER_ACCESS_TOKEN=secret

```


> run local server
```python
$ python manage.py runserver

```

> login with Eventbrite in your localhost

http://localhost:8000/

> Heroku app

https://custom-ticket-heroku.herokuapp.com/
