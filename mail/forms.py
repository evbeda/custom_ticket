from django import forms


class FormEmailSend(forms.Form):
    to_email = forms.EmailField(
        required=True,
        widget=forms.TextInput(
            attrs={'placeholder': 'Email to send to', 'class': 'form-control'}
        )
    )
    subject = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={'placeholder': 'subject', 'class': 'form-control'}
        )
    )
    message = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={'placeholder': 'Email body', 'class': 'form-control'}
        )
    )
    from_email = forms.EmailField(
        required=True,
        widget=forms.TextInput(
            attrs={'placeholder': 'Your Email', 'class': 'form-control'}
        )
    )


class FormSendEmailPreview(forms.Form):

    #   Attendee : barcode, first name, last name, cost_gross, answers
    attendee_barcode = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={'value': '752327237937711035001', 'placeholder': 'Barcode Ticket Attendee', 'class': 'form-control'}
        )
    )

    attendee_first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={'value': 'EDAc', 'placeholder': 'First Name Attendee', 'class': 'form-control'}
        )
    )

    attendee_last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={'value': 'Ticket', 'placeholder': 'Last Name Attendee', 'class': 'form-control'}
        )
    )

    attendee_cost_gross = forms.CharField(
        required=True,
        widget=forms.NumberInput(
            attrs={'value': 0.00, 'placeholder': 'Cost Gross Ticket Attendee', 'class': 'form-control'}
        )
    )

    attendee_quantity = forms.CharField(
        required=True,
        widget=forms.NumberInput(
            attrs={'value': 1, 'placeholder': 'Quantity Ticket Attendee', 'class': 'form-control'}
        )
    )

    attendee_question = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={'value': 'What is your favorite color?',
                   'placeholder': 'Question Ticket Attendee', 'class': 'form-control'}
        )
    )

    organizer_logo = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={'value': 'https://upload.wikimedia.org/wikipedia/commons/a/ab/Logo_TV_2015.png',
                   'placeholder': 'Organizer Logo URL', 'class': 'form-control'}
        )
    )

    organizer_message = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={'placeholder': 'Custom Message', 'class': 'form-control'}
        ), initial='Message body'
    )

    event_name_text = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={'value': 'EventTest_With_FreeTicket', 'placeholder': 'Event Name', 'class': 'form-control'}
        )
    )

    event_image = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={'value': 'https://cdn.pixabay.com/photo/2017/12/08/11/53/event-party-3005668_960_720.jpg',
                   'placeholder': 'Event Image URL', 'class': 'form-control'}
        )
    )
    event_start = forms.DateField(
        required=True,
        widget=forms.SelectDateWidget(
            attrs={'value': '10/10/2020', 'placeholder': 'Event Start Date', 'class': 'form-control'}
        )
    )
    event_venue_location = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={'value': 'St. Always Live 1234', 'placeholder': 'Event Venue Adress', 'class': 'form-control'}
        )
    )
    #   reserved seating
    user_order_email = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={'value': 'edacticket@gmail.com', 'placeholder': 'User Order Email', 'class': 'form-control'}
        )
    )
    #   order_id
    #   order_date
    user_order_first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={'value': 'EDAc', 'placeholder': 'User Order First Name', 'class': 'form-control'}
        )
    )
    user_order_last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={'value': 'Ticket', 'placeholder': 'User Order Last Name', 'class': 'form-control'}
        )
    )
    order_status = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={'value': 'placed', 'placeholder': 'Order Status', 'class': 'form-control'}
        )
    )
    order_created = forms.DateField(
        required=True,
        widget=forms.SelectDateWidget(
            attrs={'value': '', 'placeholder': 'Order created', 'class': 'form-control'}
        )
    )
    ticket_class = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={'value': 'FreeticketBla', 'placeholder': 'Ticket Class', 'class': 'form-control'}
        )
    )
    from_email = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={'value': 'edacticket@gmail.com', 'placeholder': 'From Email', 'class': 'form-control'}
        )
    )
    emails = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={'value': 'edacticket@gmail.com', 'placeholder': 'Emails Array', 'class': 'form-control'}
        )
    )

    email_send = forms.EmailField(
        required=True,
        widget=forms.TextInput(
            attrs={'value': 'edacticket@gmail.com', 'placeholder': 'Email Send', 'class': 'form-control'}
        )
    )
