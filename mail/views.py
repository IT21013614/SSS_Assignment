import json
import pickle

from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import HttpResponse, HttpResponseRedirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render
from mail.models import Email
from mail.models import User, Email

from django.core.mail import send_mail
from django.conf import settings
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from django.shortcuts import render

from mail.models import Email

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings


# Load the model and vectorizer
model_path = os.path.join(settings.BASE_DIR, 'mail', 'spam_classifier.pkl')
model = pickle.load(open("spam_classifier.pkl", "rb"))

feature_extraction_path = os.path.join(settings.BASE_DIR, 'mail', 'feature_extraction.pkl')
feature_extraction = pickle.load(open("feature_extraction.pkl", "rb"))


@csrf_exempt
def classify_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get("message")

        # Prepare the message for classification
        input_data_features = feature_extraction.transform([message])

        # Make the prediction
        prediction = model.predict(input_data_features)

        if prediction[0] == 1:
            return JsonResponse({"message": "This message is classified as ham."})
        else:
            return JsonResponse({"message": "This message is classified as spam."})
    else:
        return JsonResponse({"error": "POST request required."}, status=400)


def inbox(request):
    emails = Email.objects.all()
    return render(request, 'mail/inbox.html', {'emails': emails})


class IndexView(View):#displaying the inbox
    def get(self, request):
        print("IndexView.get was called") 
        if request.user.is_authenticated:
            print("User is authenticated")
            emails = Email.objects.filter(user=request.user, recipients=request.user, archived=False).order_by('-timestamp')
            print(emails) 
            return render(request, 'inbox.html', {'emails': emails})
        else:
            print("User is not authenticated")
            return HttpResponseRedirect(reverse('login'))
    #def get(self, request):
        #if request.user.is_authenticated:
            #return render(request, 'inbox.html')
        #else:
            #return HttpResponseRedirect(reverse('login'))

#def index(request):
    # Authenticated users view their inbox
    #if request.user.is_authenticated:
        #return render(request, 'inbox.html')

    # Everyone else is prompted to sign in
    #else:
        #return HttpResponseRedirect(reverse('login'))


def login_view(request):#user login process
    if request.method == 'POST':

        # Attempt to sign user in
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'login.html', {
                'message': 'Invalid email and/or password.'
            })
    else:
        return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def register(request):
    if request.method == 'POST':
        email = request.POST['email']

        # Ensure password matches confirmation
        password = request.POST['password']
        confirmation = request.POST['confirmation']
        if password != confirmation:
            return render(request, 'register.html', {
                'message': 'Passwords must match.'
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(email, email, password)
            user.save()
        except IntegrityError:
            return render(request, 'register.html', {
                'message': 'Email address already taken.'
            })
        login(request, user)
        return HttpResponseRedirect(reverse('index'))
    else:
        return render(request, 'register.html')




@login_required
def compose(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required.'}, status=400)

    emails = [email.strip() for email in request.POST.get('recipients', '').split(',')]
    if emails == ['']:
        return JsonResponse({
            'error': 'At least one recipient required.'
        }, status=400)

    # Get the file attachment
    attachment_file = request.FILES.get('attachment', None)
    attachment_path = None
    # Convert email addresses to users
    recipients = []
    for email in emails:
        try:
            user = User.objects.get(email=email)
            recipients.append(user)
        except User.DoesNotExist:
            recipients.append(None)

    

    if attachment_file:
        # Save the file to a directory
        file_path = os.path.join('attachments', attachment_file.name)
        default_storage.save(file_path, ContentFile(attachment_file.read()))

        # Store the file path in the database
        attachment_path = default_storage.path(file_path)

    # Get contents of email
    subject = request.POST.get('subject', '')
    body = request.POST.get('body', '')

    # Send email using Django's send_mail function
    try:
        send_mail(
            subject,
            body,
            settings.EMAIL_HOST_USER,
            emails,
            fail_silently=False,
        )
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    # Create one email for each recipient, plus sender
    users = set()
    users.add(request.user)
    users.update(recipients)
    for user in users:
        if user is not None:
            email = Email(
                user=user,
                sender=request.user,
                subject=subject,
                body=body,
                attachment=attachment_path,  # Add this line
                read=user == request.user
            )
            email.save()
            for recipient in recipients:
                if recipient is not None:
                    email.recipients.add(recipient)
        email.save()




    
    

    return JsonResponse({'message': 'Email sent successfully.'}, status=201)



@login_required
def mailbox(request, mailbox):

    # Filter emails returned based on mailbox
    if mailbox == 'inbox':
        emails = Email.objects.filter(
            recipients=request.user, archived=False
        )
    elif mailbox == 'sent':
        emails = Email.objects.filter(
            user=request.user, sender=request.user
        )
    elif mailbox == 'archive':
        emails = Email.objects.filter(
            user=request.user, recipients=request.user, archived=True
        )
    else:
        return JsonResponse({'error': 'Invalid mailbox.'}, status=400)

    # Return emails in reverse chronologial order
    emails = emails.order_by('-timestamp').all()
    print("Emails: ", emails)
    return JsonResponse([email.serialize() for email in emails], safe=False)


@csrf_exempt
@login_required
def email(request, email_id):

    # Query for requested email
    try:
        email = Email.objects.get(user=request.user, pk=email_id)
    except Email.DoesNotExist:
        return JsonResponse({'error': 'Email not found.'}, status=404)

    # Return email contents
    if request.method == 'GET':
        return JsonResponse(email.serialize())

    # Update whether email is read or should be archived
    elif request.method == 'PUT':
        data = json.loads(request.body)
        if data.get('read') is not None:
            email.read = data['read']
        if data.get('archived') is not None:
            email.archived = data['archived']
        email.save()
        return HttpResponse(status=204)

    # Email must be via GET or PUT
    else:
        return JsonResponse({
            'error': 'GET or PUT request required.'
        }, status=400)
