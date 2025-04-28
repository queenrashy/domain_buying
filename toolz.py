import re
import string
import random

from flask_mail import Message
from app import mail
from config import Config
def is_valid_email(email):
    if email is None:
        return False
    # Regular expression pattern for validating an email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+.[a-zA-Z]{2,}$'
    
    # Match the email against the pattern
    if re.match(pattern, email):
        return True
    else:
        return False
    
    
# generate a random number for the token

def random_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
    

# send email function

def send_email(subject, receiver, text_body, html_body):
    msg = Message(subject=subject, sender=('Queen', Config.MAIL_USERNAME), recipients=[receiver])
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)