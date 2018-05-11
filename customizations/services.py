import cStringIO
from django.db import (
    DatabaseError,
    transaction,
)
from django.shortcuts import (
    get_object_or_404,
)


from customizations.models import (
    BaseTicketTemplate,
    Customization,
    CustomEmail,
    TicketTemplate,
    UserWebhook,
)

from customizations.utils import (
    create_webhook,
    get_token,
    get_image_and_save,
    upload_file_dropbox,
)


def compose_customization(dto, user, links_logo):
    has_image = bool(dto.image_data)
    if has_image:
        img_content = get_image_and_save(
            dto.image_data,
            user
        )
        name_image = img_content.name
    image_has_content = img_content is not None
    try:
        with transaction.atomic():
            template = BaseTicketTemplate.objects.get(
                pk=dto.select_design_template
            )
            ticket = TicketTemplate.objects.create(
                select_design_template=template,
                message_ticket=dto.message_ticket,
                show_event_sequence=dto.show_event_sequence,
                show_ticket_type_sequence=dto.show_ticket_type_sequence,
                hide_ticket_type_price=dto.hide_ticket_type_price,
                footer_description=dto.footer_description,
                double_ticket=dto.double_ticket,
            )
            if has_image and image_has_content:
                custom_email = CustomEmail.objects.create(
                    message=dto.message,
                    logo=links_logo['dropbox'],
                    logo_local=links_logo['local'],
                    logo_path=links_logo['path'],
                    logo_name=links_logo['name'],
                    logo_url=links_logo['dropbox'],
                    image_partner=img_content,
                    image_partner_name=name_image,
                )
                url = upload_file_dropbox(
                    custom_email.image_partner.path,
                    img_content.name
                )
            else:
                custom_email = CustomEmail.objects.create(
                    message=dto.message,
                    logo=links_logo['dropbox'],
                    logo_local=links_logo['local'],
                    logo_path=links_logo['path'],
                    logo_name=links_logo['name'],
                    logo_url=links_logo['dropbox'],
                )
            customization = Customization.objects.create(
                user=user,
                ticket_template=ticket,
                custom_email=custom_email,
                name=dto.name_customization,
                pdf_ticket_attach=dto.pdf_ticket_attach,
            )

            if has_image and image_has_content:
                query = CustomEmail.objects.get(
                    pk=customization.custom_email.id
                )
                query.image_partner_local = custom_email.image_partner.url
                query.image_partner_url = url
                query.image_partner_path = custom_email.image_partner.path
                query.save()

            if not UserWebhook.objects.filter(user=user).exists():
                token = get_token(user)
                webhook_id = create_webhook(token)
                UserWebhook.objects.create(
                    user=user,
                    webhook_id=webhook_id,
                )

            return {
                'status': True,
            }

    except DatabaseError as err:

        return {
            'status': False,
            'error': 'DatabaseError: ' + err.message
        }


def edit_customization(
    dto,
    links_logo,
    user,
):
    img_content = get_image_and_save(
        dto.image_data,
        user,
    )
    try:
        with transaction.atomic():
            dto.customization.name = dto.name_customization
            if dto.logo is not None:
                dto.custom_email.logo = links_logo['dropbox']
                dto.custom_email.logo_local = links_logo['local']
                dto.custom_email.logo_path = links_logo['path']
                dto.custom_email.logo_name = links_logo['name']
                dto.custom_email.logo_url = links_logo['dropbox']
            dto.customization.pdf_ticket_attach = dto.pdf_ticket_attach
            dto.custom_email.message = dto.message
            if img_content is not None:
                dto.custom_email.image_partner = img_content
                dto.custom_email.image_partner_name = img_content.name

            dto.ticket_template.select_design_template = get_object_or_404(
                BaseTicketTemplate,
                pk=dto.select_design_template
            )
            dto.ticket_template.message_ticket = dto.message_ticket
            dto.ticket_template.footer_description = dto.footer_description
            dto.ticket_template.show_event_sequence = dto.show_event_sequence
            dto.ticket_template.show_ticket_type_sequence = dto.show_ticket_type_sequence
            dto.ticket_template.hide_ticket_type_price = dto.hide_ticket_type_price
            dto.ticket_template.double_ticket = dto.double_ticket
            dto.custom_email.save()
            dto.ticket_template.save()
            dto.customization.save()
            if img_content is not None:
                url = upload_file_dropbox(
                    dto.custom_email.image_partner.path,
                    img_content.name
                )
                query = CustomEmail.objects.get(
                    pk=dto.customization.custom_email.id
                )
                query.image_partner_local = dto.custom_email.image_partner.url
                query.image_partner_url = url
                query.image_partner_path = dto.custom_email.image_partner.path
                query.save()
            return True

    except DatabaseError:
        return False
