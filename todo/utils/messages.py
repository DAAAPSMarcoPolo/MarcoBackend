from django.conf import settings
from django.core.mail import EmailMessage

class Utils:
  def send_email(self, message, subject, recipients):
    email = EmailMessage(subject, message, to=recipients)
    email.send()
    return