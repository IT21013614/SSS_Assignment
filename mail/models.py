from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    def __str__(self):
        return f'{self.username}'

class Email(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emails')
    sender = models.ForeignKey(User, on_delete=models.PROTECT, related_name='emails_sent')
    recipients = models.ManyToManyField(User, related_name='emails_received')
    subject = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    date = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    attachment = models.FileField(upload_to="attachments/", null=True, blank=True)
    is_spam = models.BooleanField(default=False)

    def serialize(self):
        return {
            'id': self.id,
            'sender': self.sender.email,
            'recipients': [user.email for user in self.recipients.all()],
            'subject': self.subject,
            'body': self.body,
            'timestamp': self.timestamp.strftime('%b %d %Y, %I:%M %p'),
            'read': self.read,
            'archived': self.archived,
            'is_spam': self.is_spam
        }