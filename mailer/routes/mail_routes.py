from flask import Blueprint, current_app, jsonify, request

from email_service.sender import send_email

mail_blueprint = Blueprint('mail', __name__)

@mail_blueprint.route('/send', methods=['POST'])
def send_mail():
    content = request.json
    current_app.logger.info(content)
    sender = content['sender']
    recipients = content['recipients']
    subject = content['subject']
    body = content['body']
    attachments = content['attachments']

    current_app.logger.info('Sending email')
    send_email(subject=subject, sender=sender, body=body, recipients=recipients, attachments=attachments)
    return jsonify({'message': 'Email sent'})
