from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.core.mail import send_mail

from datetime import datetime, timedelta
import pytz

from functools import reduce

import dropbox

from .models import UserData, UploadedFile, Message


def findStudent(name = '', view=''):

    if view == 'findall':
        return list(map(lambda x: {'username': x.username, 'id': x.id}, UserData.objects.filter(is_superuser = False, validated = True, username__icontains=name)))

    elif view == 'fees':
        params = ['id', 'username', 'no_of_class_attended', 'last_fees_paid']
        
    elif view == 'attendance':
        params = ['username', 'id', 'no_of_class_attended', 'last_class_attended']

    elif view == 'student-data':
        params = ['id', 'username', 'phone_number', 'no_of_class_attended', 'last_class_attended']

    elif view == 'delete':
        params = ['id', 'username']
    
    batch1 = list(map(lambda x: {param:x[param] for param in params}, UserData.objects.filter(username__icontains=name, is_superuser = False, validated = True, batch_number=1).values()))
    batch2 = list(map(lambda x: {param:x[param] for param in params}, UserData.objects.filter(username__icontains=name, is_superuser = False, validated = True, batch_number=2).values()))

    return {'batch1':batch1, 'batch2': batch2}

def sendMail(user):
    subject = str(user.username) + " account details."
    body = "User password : " + str(user.password)
    sender = settings.EMAIL_HOST_USER
    receiver = user.email_address
    send_mail(subject, body, sender, [receiver, ])


def deleteOldMessages():
    deleteThreshold = getTime() - timedelta(weeks=3)
    old_messages = Message.objects.filter(datePosted__lte=deleteThreshold)

    for message in old_messages:
        message.delete()


def errorMessage(request, errorCode=None):
    if errorCode == 'notSignedIn':
        messages.info(request, "You have logged out. Please login again to access content")
        return redirect('home')

    elif errorCode == 'notValidated':
        messages.info(request,
                      'Looks like the teacher has not approved of your account yet. Please try again later or contact the teacher.')

    elif errorCode == 'accountExists':
        messages.info(request, 'Looks like there is an account with these credentials already.')
        return redirect('login')

    elif errorCode == 'wrongPassword':
        messages.info(request, 'Please enter the correct password')

def checkStatus(request, sudo=False):
    userId = request.session.get('user_info')
    try:
        user = UserData.objects.get(id=userId)
        if userId is not None and userId is not -1:
            if user.is_superuser:
                if sudo:
                    return "superuser"
                else:
                    return False
            else:
                return True
        else:
            return False
    except:
        return False


def getTime():
    return datetime.now(tz=pytz.timezone('Asia/Kolkata')) + timedelta(hours=5, minutes=30)

def authenticate(request, phone_number=None, password=None):
    try:
        user = UserData.objects.get(phone_number=phone_number)
    except:
        messages.info(request, "Phone number invalid. Please try with registered phone number.")
        return "None"

    if user.validated == True:
        if password == user.password:
            user.is_logged_in = True
            user.save()

        else:
            if password != user.password:
                errorMessage(request, "wrongPassword")
            else:
                errorMessage(request, "notValidated")
            return "None"

        if user.is_superuser == True:
            return "Yes"
        else:
            return "No"

        return "None"
    else:
        messages.info(request, "Please wait until the admin validates your account")
        return "None"

def sendMessage(sender_id, message, recipients):
    for user in recipients:
        user.unseen_message_count += 1
        user.save()

    sender = UserData.objects.get(id=sender_id)

    message = Message(message=message, sender=sender, datePosted=getTime())
    message.save()
    for recipient in recipients:
        message.allowedUsers.add(recipient)

# Function to mark attendance of all the present students
# Used in attendance_view
def markPresent(present):
    for id in present:
        person = UserData.objects.get(id=id)
        person.last_class_attended = getTime()
        person.no_of_class_attended += 1
        person.save()



# Dropbox file media related function
def dropboxLogin():
    if settings.DEBUG:
        from .dropboxKey import getDropboxAPIKey
        dbx = dropbox.Dropbox(getDropboxAPIKey())
    else:
        import os
        dbx = os.environ.get('DROPBOX_API_KEY', None)
    return dbx

# Used in admin_upload_file_view
def upload(description, recipients, upload_file):
    
    dbx = dropboxLogin()
    
    try:
        dbx.files_upload(upload_file.read(), '/'+str(upload_file), mode = dropbox.files.WriteMode('overwrite'))
    except dropbox.exceptions.ApiError as err:
        if (err.error.is_path() and err.error.get_path().reason.is_insufficient_space()):
            print("ERROR: Cannot back up; insufficient space.")
        elif err.user_message_text:
            print(err.user_message_text)
        else:
            print(err)

    newFile = UploadedFile(description=description, fileName=str(upload_file))
    newFile.save()
    for recipient in recipients:
        newFile.allowedUsers.add(recipient)

# Used by student_download_view and admin_view_file_view
def download(name):
    dbx = dropboxLogin()
    try:
        md, res = dbx.files_download('/'+name)
    except dropbox.exceptions.HttpError as err:
        print('*** HTTP error', err)
        return None

    print(res)
    data = res.content

    response = HttpResponse(data)
    response['Content-Disposition'] = 'attachment; filename=' + name
    return response

    raise Http404

# Function to delete old files once storage space starts running out
#TODO: Implement auto-delete
def deleteOldFiles():
    dbx = dropboxLogin()
    spaceUsage = str(dbx.users_get_space_usage()).split('=')
    usedSpace = int(spaceUsage[1].split(',')[0])
    totalSpace = int(spaceUsage[-1].split(')')[0])
    percentageUsed = usedSpace/totalSpace

    if percentageUsed > 0.9:
        pass