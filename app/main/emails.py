from flask_mail import Message
from app import mail

def send_email(subject, sender, recipients, body):
    msg = Message(subject, sender=sender, recipients=[recipients])
    msg.body = body
    mail.send(msg)