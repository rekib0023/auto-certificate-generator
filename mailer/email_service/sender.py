from email.message import EmailMessage
import ssl
import smtplib
import os
from flask import current_app, render_template
from typing import Dict, List
from utils.s3 import S3Instance

def send_email(subject: str, sender: str, body: str, recipients: List[str], attachments: List[Dict[str, str]]=None):
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(os.environ['MAIL_USERNAME'], os.environ['MAIL_PASSWORD'])
        for recipient, attachment in zip(recipients, attachments):
            em = EmailMessage()
            em['From'] = sender
            em['To'] = recipient
            em['Subject'] = subject
            em.set_content(body)

            html_template = render_template("certificate_mail.html", recipient=recipient)
            em.add_alternative(html_template, subtype='html')

            s3_obj = S3Instance()
            bucket = s3_obj.bucket_name
            s3_obj = s3_obj.client
            response = s3_obj.get_object(Bucket=bucket, Key=attachment['key'])
            attachment_data = response['Body'].read()
            
            em.add_attachment(attachment_data, maintype=attachment['mime_type'],
                            subtype=attachment['subtype'], filename=attachment['filename'])
            try:
                smtp.sendmail(sender, recipients[0], em.as_string())
            except Exception as error:
                current_app.logger.error(f"Failed to send email to {recipient}, error: ", error)
