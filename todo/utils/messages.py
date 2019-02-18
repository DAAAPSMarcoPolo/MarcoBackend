from django.conf import settings
from django.core.mail import EmailMessage

import requests

class Utils:
  def send_email(self, message, subject, recipients):
    return requests.post(
      settings.EMAIL_DOMAIN,
      auth=("api", settings.EMAIL_KEY),
      data={"from": settings.EMAIL_FROM,
            "to": recipients,
            "subject": subject,
            "text": message})