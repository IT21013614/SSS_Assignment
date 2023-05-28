import imaplib
import email
from email.header import decode_header
import webbrowser
import os

# your email, password, and the IMAP server
email_user = os.getenv('EMAIL_USER')
email_pass = os.getenv('EMAIL_PASS')
imap_server = os.getenv('IMAP_SERVER')
mail = imaplib.IMAP4_SSL(imap_server)
# authenticate
mail.login(email_user, email_pass)

# select the mailbox you want to delete in
# if you want SPAM, use "INBOX.SPAM"
# use "INBOX" to read inbox emails
mail.select("inbox")

# get all mail IDs
result, data = mail.uid('search', None, "ALL")
mail_ids = data[0]
id_list = mail_ids.split()
latest_email_id = int(id_list[-1])

# loop through each email id to fetch the email data
for i in range(latest_email_id, latest_email_id-5, -1): # I am fetching last 5 emails here
    result, data = mail.uid('fetch', str(i).encode(), '(BODY.PEEK[HEADER])')

    raw_email = data[0][1].decode("utf-8")
    email_message = email.message_from_string(raw_email)

    print("\n\n---- Mail Start ----\n\n")
    
    # decode the email subject
    subject = decode_header(email_message['Subject'])[0][0]
    if isinstance(subject, bytes):
        # if it's a bytes type, decode to str
        subject = subject.decode()
    print("Subject:", subject)

    # decode the email sender
    from_ = decode_header(email_message['From'])[0][0]
    if isinstance(from_, bytes):
        from_ = from_.decode()
    print("From:", from_)

    print("\n---- Mail End ----\n\n")

# close the connection
mail.logout()
