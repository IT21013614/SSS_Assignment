from mail.models import Email
from imapclient import IMAPClient
import email
from email.header import decode_header


username='test1sssmod@gmail.com'
password='ubmcimkxzaeyllhi'

def fetch_and_save_emails(username, password, server='imap.gmail.com'):
    # connect to the server
    client = IMAPClient(server)
    
    # login to the server
    client.login(username, password)
    
    # select the mailbox you want to delete in
    # if you want SPAM, use "INBOX.SPAM"
    client.select_folder('INBOX')

    # get uids of all messages in the inbox
    messages = client.search()
    
    for uid, message_data in client.fetch(messages, 'BODY.PEEK[]').items():
        email_message = email.message_from_bytes(message_data[b'BODY[]'])
        subject = decode_header(email_message.get('Subject'))[0][0]
        if isinstance(subject, bytes):
            # if it's a bytes type, decode to str
            subject = subject.decode()
        sender = decode_header(email_message.get('From'))[0][0]
        if isinstance(sender, bytes):
            # if it's a bytes type, decode to str
            sender = sender.decode()
        date = email_message.get('Date')
        body = ""
        if email_message.is_multipart():
            for part in email_message.get_payload():
                if part.get_content_type() == 'text/plain':
                    body = part.get_payload()
        else:
            body = email_message.get_payload()
        new_email = Email(subject=subject, sender=sender, body=body, date=date)
        new_email.save()
    client.logout()
