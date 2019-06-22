from .forms import *
from .models import Message, storeData, FileUpload
import os
from django.contrib import messages
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.conf import settings
from django.http import HttpResponse, Http404
from datetime import datetime, timedelta, time
from django.utils import timezone

import pytz 
from django.core.mail import send_mail
 
# The base home page which leads to login/sign up pages
def home(request):          
    try:
        userId = request.session.get('user_info')
        user = storeData.objects.get(id=userId)

        if user.is_logged_in:
            if user.is_superuser:
                return redirect('adminhome')
            else:
                return redirect('studenthome')
        else:
            messages.info(request, "Please login to access the website")
            return render(request, 'home.html')
    except:
        return render(request, 'home.html')


# The page to log in. Handles superusers(admins) and normal users(students) separately
def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            phone_number = request.POST.get('phone_number')
            password = request.POST.get('password')

            response = authenticate(request, phone_number=phone_number, password=password)

            if response == 'Yes':         
                user = storeData.objects.get(phone_number = phone_number)
                request.session['user_info'] = user.id
                return redirect('/admin-home/')

            elif response == "No":
                user = storeData.objects.get(phone_number = phone_number)
                request.session['user_info'] = user.id
                return redirect('/student-home/')

            else:
                return redirect('/')
        
        else:
            print(form.errors)
    
    else:
        form = LoginForm()
    
    return render(request, 'Registry/login.html', {"form": form})

# Function to register new users..
def register(request):
    if request.method =='POST':
        form = RegistrationForm(request.POST)
        
        if form.is_valid():

            #Extract relevant data from the form
            username = request.POST.get('username')
            password = request.POST.get('password')
            phone = request.POST.get('phone_number')
            Batch = request.POST.get('Batch')
            confirm_password = request.POST.get('confirm_password')
            email_address = request.POST.get('email_address')
            if password == confirm_password:
                try:
                    user = storeData.objects.get(username = username, phone_number = phone)
                    phone_number = storeData.objects.get(phone_number = phone)
                    errorMessage(request, 'accountExists')
                    return HttpResponseRedirect('/')                
                
                except:
                    newUser = storeData(username = username, password = password, phone_number = phone, batch_number = Batch, email_address = email_address)
                    newUser.save()
                    messages.info(request, 'Your registration is complete. Please wait for the administrator to validate your account')
                    return HttpResponseRedirect('/')
                
            else:
                messages.info(request, "Password confirmation incorrect")
                return HttpResponseRedirect('/')
    
    else:
        form = RegistrationForm()
    
    args = {'form': form}
    
    return render(request, 'Registry/signup.html', args)


# Leads to the home page for the admin, where all the attendance, fees and other activities are there
def loginAdminHome(request):
    if checkStatus(request, sudo = True) == "superuser":
        appearance = False
        
        
        if storeData.objects.filter(validated=0):
            appearance = True

        print("Appearance: ",appearance)
        currentTime = getTime()
        deleteThreshold = currentTime - timedelta(weeks = 8)
        old_files = []
        old_files = FileUpload.objects.filter(upload_time__lte = deleteThreshold)
        deleteOldFiles(old_files)

        user = storeData.objects.get(id = request.session.get('user_info'))
        args = {'requiresValidation': appearance, 'messagesUnseen': user.unseen_message_count, 'total':user.unseen_message_count+user.unseen_file_count}
        return render(request, 'Registry/adminBase.html', args)
    else:
        errorMessage(request, 'notSignedIn')
        return redirect('home')


#The home page for the students.
def loginStudentHome(request):

    if checkStatus(request):

        userData = {'id': None, 'name': '', 'classesAttended': None, 'lastAttended': None, 'feesStatus': False}
        try:
            user_id = request.session.get('user_info')
            user = storeData.objects.get(id = user_id)  
            userData['id'] = user.id
            userData['name'] = user.username
            userData['classesAttended'] = user.no_of_class_attended
            userData['lastAttended'] = user.last_class_attended.date()
            userData['feesStatus'] = user.last_fees_paid.date()
            userData['messagesUnseen'] = user.unseen_message_count
            userData['filesUnseen'] = user.unseen_file_count
            userData['total'] = user.unseen_file_count + user.unseen_message_count
            
            return render(request, 'Registry/studentBase.html', userData)
        except:
            errorMessage(request, "notSignedIn")
            return redirect('home')
    
    errorMessage(request, 'notSignedIn')
    return redirect('home')

# Show basic data like the email id and the phone number details(Admin page)
def studentsData(request):

    if checkStatus(request, sudo = True) == "superuser":
        args = {'batch1':[], 'batch2': []}
        
        for user in storeData.objects.values():
        
            if not user['is_superuser'] and user['validated']:
        
                temp = {'id': None, 'name': '', 'phoneNumber': '', 'classesAttended': None, 'lastAttended': None, 'feesStatus': False, 'isValidated': False}
                
                temp['id'] = (user['id'])
                temp['name'] = (user['username'])
                temp['phoneNumber'] = (user['phone_number'])
                temp['classesAttended'] = (user['no_of_class_attended'])
                temp['lastAttended'] = (user['last_class_attended'].date())

                if user['batch_number'] == 1:
                    args['batch1'].append(temp)
                else:
                    args['batch2'].append(temp)
        
        return render(request, 'Registry/studentsData.html', args)
    else:
        errorMessage(request, 'notSignedIn')
        return redirect('home')


# Mark and store the attendance functionalities(Admin page)
def attendance(request):

    if checkStatus(request, sudo = True) == "superuser":
        args = {}

        if request.method == 'POST':
            if 'attendance' in request.POST:
                present = []
                form = AttendanceForm(request.POST)

                if form.is_valid:
                    for user in storeData.objects.values():
                        if request.POST.get(str(user['id'])):
                            present.append(user['id'])

                    markPresent(present)
                    return redirect('studentsData')
                    
            if 'search' in request.POST:
                LIST_OF_CHOICES_1 = []
                LIST_OF_CHOICES_2 = []
                search = request.POST.get("search_field")
                similar_users = storeData.objects.filter(username__icontains=search)
                similar_users = similar_users.values()
                form = AttendanceForm()
                for user in similar_users:
                    if not user['is_superuser'] and user['validated']:
                        if user['batch_number'] == 1:
                            LIST_OF_CHOICES_1.append({'name': user['username'], 'id': user['id'], 'number': user['no_of_class_attended'], 'lastAttended': user['last_class_attended'].date()})
                        else:
                            LIST_OF_CHOICES_2.append({'name': user['username'], 'id': user['id'], 'number': user['no_of_class_attended'], 'lastAttended': user['last_class_attended'].date()})

                args = {'form': form ,'students': {"batch1": LIST_OF_CHOICES_1, "batch2": LIST_OF_CHOICES_2}}

                return render(request, 'Registry/attendance.html', args)
        else:
            LIST_OF_CHOICES_1 = []
            LIST_OF_CHOICES_2 = []
            form = AttendanceForm()
            for user in storeData.objects.values():
                if not user['is_superuser'] and user['validated']:
                    if user['batch_number'] == 1:
                        LIST_OF_CHOICES_1.append({'name': user['username'], 'id': user['id'], 'number': user['no_of_class_attended'], 'lastAttended': user['last_class_attended'].date()})
                    else:
                        LIST_OF_CHOICES_2.append({'name': user['username'], 'id': user['id'], 'number': user['no_of_class_attended'], 'lastAttended': user['last_class_attended'].date()})

            args = {'form': form ,'students': {"batch1": LIST_OF_CHOICES_1, "batch2": LIST_OF_CHOICES_2}}

        return render(request, 'Registry/attendance.html', args)
    else:
        errorMessage(request, 'notSignedIn')
        return redirect('home')



# The last fees paid date
def fees(request):
    if checkStatus(request, sudo = True) == "superuser":
        args = {}

        if request.method == 'POST':
            if 'fees' in request.POST:
                present = []
                form = AttendanceForm(request.POST)

                if form.is_valid:
                    for user in storeData.objects.values():
                        if request.POST.get(str(user['id'])):
                            User = storeData.objects.get(id = str(user['id']))
                            User.last_fees_paid = getTime()
                            User.save()
                            
                    return redirect('fees')
            if 'search' in request.POST:
                LIST_OF_CHOICES_1 = []
                LIST_OF_CHOICES_2 = []
                search = request.POST.get("search_field")
                similar_users = storeData.objects.filter(username__icontains=search)
                similar_users = similar_users.values()
                form = AttendanceForm()
                for user in similar_users:
                    if not user['is_superuser'] and user['validated']:
                        if user['batch_number'] == 1:
                            LIST_OF_CHOICES_1.append({'name': user['username'], 'id': user['id'], 'number': user['no_of_class_attended'], 'lastFeesPaid': user['last_fees_paid'].date()})
                        else:
                            LIST_OF_CHOICES_2.append({'name': user['username'], 'id': user['id'], 'number': user['no_of_class_attended'], 'lastFeesPaid': user['last_fees_paid'].date()})

                args = {'form': form ,'students': {"batch1": LIST_OF_CHOICES_1, "batch2": LIST_OF_CHOICES_2}}

                return render(request, 'Registry/fees.html', args)
        else:
            LIST_OF_CHOICES_1 = []
            LIST_OF_CHOICES_2 = []
            form = AttendanceForm()
            for user in storeData.objects.values():
                if not user['is_superuser'] and user['validated']:
                    if user['batch_number'] == 1:
                        LIST_OF_CHOICES_1.append({'name': user['username'], 'id': user['id'], 'number': user['no_of_class_attended'], 'lastFeesPaid': user['last_fees_paid'].date()})
                    else:
                        LIST_OF_CHOICES_2.append({'name': user['username'], 'id': user['id'], 'number': user['no_of_class_attended'], 'lastFeesPaid': user['last_fees_paid'].date()})

            args = {'form': form ,'students': {"batch1": LIST_OF_CHOICES_1, "batch2": LIST_OF_CHOICES_2}}

        return render(request, 'Registry/fees.html', args)
    else:
        errorMessage(request, 'notSignedIn')
        return redirect('home')


def validateStudent(request):
    if checkStatus(request, sudo = True) == "superuser":
        if request.method == 'POST':
            form = ValidationForm(request.POST)
            if form.is_valid:
                for user in storeData.objects.values():
                    response = request.POST.get(str(user['id']))
                    student = storeData.objects.get(id = str(user['id']))
                    if(response == "Accept"): 
                        student.validated = True
                        student.save()
                    elif(response == "Delete"):
                        student.delete()
                return redirect('adminhome')
            #List of unvalidated users.
        else:
            form = ValidationForm()
            users = []
            delete = []
            for user in storeData.objects.values():
                if(user['validated'] == False):
                    users.append({'name': user['username'], 'batch': user['batch_number'], "id": user['id']})

                if(user['is_superuser'] == False):
                    delete.append({'name': user['username'], 'batch': user['batch_number'], 'id': user['id']})

        return render(request, 'Registry/validate.html', {'users': users})
    else:
        errorMessage(request, 'notSignedIn')
        return redirect('home')


def adminViewMessage(request):
    if checkStatus(request, sudo = True) == "superuser":
        final = {'received': [], 'sent': []}
        user = storeData.objects.get(is_superuser = 1)
        user.unseen_message_count = 0
        user.save()
        id = 0

        currentTime = getTime()     #Is 5 hours and 30 minutes ahead of datetime.now()
    
        displayThreshold = currentTime - timedelta(weeks = 1)
        new_message = []
        new_message = Message.objects.filter(datePosted__gte= displayThreshold)

        deleteThreshold = currentTime - timedelta(weeks = 3)
        old_message = []
        old_message = Message.objects.filter(datePosted__lte = deleteThreshold)

        deleteOldMessage(old_message)
        
        for message in new_message:

            if message.sender == str(user.username):
                final['sent'].append({'id': str(id), 'brief': message.message[:10]+"...", 'posts': message.message, 'dates': str(message.datePosted.date())})


            if str(user.username) in (message.allowedUsers):
                final['received'].append({'id': str(id), 'brief': message.message[:10]+"...",  'posts': message.message, 'dates': str(message.datePosted.date()), 'sender': str(message.sender)})
            id += 1
        return render(request, 'Registry/adminViewMessage.html', final)
    else:
        errorMessage(request, 'notSignedIn')
        return redirect('home')



# View for message broadcasting
def adminSendMessage(request):
    if checkStatus(request, sudo=True):
        args = {}
        if request.method == 'POST':
            if 'send' in request.POST:
                recipients = []
                form = SelectStudentForm(request.POST)
                
                if form.is_valid:
                    message = request.POST['message']
                    
                    if request.POST.get('selectall'):
                        recipients = storeData.objects.filter(is_superuser = 0)
                        recipients = recipients.values()

                    elif request.POST.get('batch1'):
                        recipients = storeData.objects.filter(batch_number = 1)
                        recipients = recipients.values()
                    
                    elif request.POST.get('batch2'):
                        recipients = storeData.objects.filter(batch_number = 2)
                        recipients = recipients.values()

                    else:
                        for user in storeData.objects.values():
                            if request.POST.get(str(user['id'])):
                                recipients.append(user)
                    
                    # Function to save the the message to the database
                    sendMessage(request, message, recipients)
                    messages.info(request, 'Message has been sent.')
                    
                    return redirect('adminhome')
            if 'search' in request.POST:
                form = SelectStudentForm()
                LIST_OF_CHOICES = []
                search = request.POST.get("search_field")
                similar_users = storeData.objects.filter(username__icontains=search)
                similar_users = similar_users.values()
                for user in similar_users:
                    if not user['is_superuser'] and user['validated']:
                        LIST_OF_CHOICES.append(user)

                args = {"form": form, "students": LIST_OF_CHOICES}

                return render(request, 'Registry/adminSendMessage.html', args)
        else:
            form = SelectStudentForm()
            LIST_OF_CHOICES = []

            for user in storeData.objects.values():
                if not user['is_superuser'] and user['validated']:
                    LIST_OF_CHOICES.append(user)

            args = {"form": form, "students": LIST_OF_CHOICES}

        return render(request, 'Registry/adminSendMessage.html', args)
    else:
        errorMessage(request, 'notSignedIn')
        return redirect('home')


def adminViewFile(request):

    if checkStatus(request, sudo = True) == "superuser":
        args = {'Files': []}
        userId = request.session.get('user_info')
        user = storeData.objects.get(id = userId)
        if request.method == 'POST':
            form = FileDownloadForm(request.POST)

            if form.is_valid():
                id = int(request.POST.get('fileField'))
                return download(id)

        else:
            for File in FileUpload.objects.values():
                args["Files"].append({"id": File["id"], "name": os.path.basename(FileUpload.objects.get(id = File['id']).uploadedFile.path), "date": str(File['upload_time'].date()), 'description': File['description']})

            return render(request, 'Registry/adminViewFile.html', args)
        
    else:
        errorMessage(request, 'notSignedIn')
        return redirect('home')

# Function to upload files to the system
def adminUploadFile(request):
    if checkStatus(request, sudo = True) == "superuser":
        args = {}

        if request.method == 'POST':
            if 'upload' in request.POST:
                recipients = []
                form = FileUploadForm(request.POST, request.FILES)

                if form.is_valid():
                    form.save()
                    
                    if request.POST.get('selectall'):
                        recipients = storeData.objects.filter(is_superuser = 0)
                        recipients = recipients.values()

                    elif request.POST.get('batch1'):
                        recipients = storeData.objects.filter(batch_number = 1)
                        recipients = recipients.values()
                    
                    elif request.POST.get('batch2'):
                        recipients = storeData.objects.filter(batch_number = 2)
                        recipients = recipients.values()

                    else:
                        for user in storeData.objects.values():
                            if request.POST.get(str(user['id'])):
                                recipients.append(user)
                    
                    upload(recipients)
                    messages.info(request, 'File has been uploaded.')
                    return redirect('adminhome')
                else:
                    return redirect('adminUploadFile')

            if 'search' in request.POST:
                form = FileUploadForm()
                LIST_OF_CHOICES = []
                search = request.POST.get("search_field")
                similar_users = storeData.objects.filter(username__icontains=search) 
                for user in similar_users:
                    if not user.is_superuser:
                        LIST_OF_CHOICES.append(user)

                args = {"form": form, "students": LIST_OF_CHOICES}
                return render(request, 'Registry/adminUploadFile.html', args)
        else:
            form = FileUploadForm()
            LIST_OF_CHOICES = []

            for user in storeData.objects.values():
                if not user['is_superuser']:
                    LIST_OF_CHOICES.append(user)

            args = {"form": form, "students": LIST_OF_CHOICES}
            print("Here")
            return render(request, 'Registry/adminUploadFile.html', args)
    else:
        errorMessage(request, 'notSignedIn')
        return redirect('home')

# Function for the student to send message to the teacher/superusers
def studentSendMessage(request):
    
    if checkStatus(request):
        args = {}
        
        if request.method == 'POST':
        
            form = SelectStudentForm(request.POST)
        
            if form.is_valid:
        
                message = request.POST['message']

                for user in storeData.objects.values():
                    if user['is_superuser'] == True:
                        admin = user
                        user['unseen_message_count'] += 1
                        storeData.objects.get(is_superuser = True).save()
                l = []
                l.append(admin)
        
                #invoke the message sending function   
                sendMessage(request, message, l)
        
                messages.info(request, 'Message has been sent.')
        
                return redirect('/student-home')
        
        else:
        
                form = SelectStudentForm()
                args = {"form": form}
        return render(request, 'Registry/studentSendMessage.html', args)
    
    errorMessage(request, 'notSignedIn')
    return redirect('home')
    

# A function for the students to see the messages sent by the admin
def studentViewMessage(request):

    if checkStatus(request):
        try: 
            userId = request.session.get('user_info')
            user = storeData.objects.get(id = userId)
            print(user.username)
            user.unseen_message_count = 0
            user.save()
            final = {'received': [], 'sent': []}
            countSent = 0
            countRcv = 0
            id = 0
            for message in Message.objects.values():
                if countSent < 3:
                    if message['sender'] == str(user.username):
                        final['sent'].append({'id': str(id), 'brief': message['message'][:10]+"...", 'posts': message['message'], 'dates': str(message['datePosted'].date())})
                        countSent = countSent + 1
                if countRcv < 3:
                    if str(user.username) in (message['allowedUsers']):
                        final['received'].append({'id': str(id), 'brief': message['message'][:10]+"...",  'posts': message['message'], 'dates': str(message['datePosted'].date()), 'sender': str(message['sender'])}) 
                        countRcv += 1
                    id += 1
                if countRcv == 4 or countSent == 4:
                    break
            return render(request, 'Registry/studentViewMessage.html', final)
        except:
            errorMessage(request, 'notSignedIn')
            return redirect('home')
    errorMessage(request,  'notSignedIn')
    return redirect('home')

def downloadFile(request):
    args = {"Files": []}
    userId = request.session.get('user_info')
    user = storeData.objects.get(id = userId)
    user.unseen_file_count = 0
    user.save()

    if checkStatus(request):
        if request.method == 'POST':
            form = FileDownloadForm(request.POST)

            if form.is_valid():
                id = int(request.POST.get('fileField'))
                return download(id)
        else:
            for File in FileUpload.objects.values():
                if str(user.username) in File['allowedUsers']:
                    args["Files"].append({"id": File["id"], "name": os.path.basename(FileUpload.objects.get(id = File['id']).uploadedFile.path), "date": str(File['upload_time'].date())})

            return render(request, 'Registry/downloadFile.html', args)
    
    else:
        errorMessage(request,  'notSignedIn')
        return redirect('home')


# Function to verify if the password is correct or wrong. Further checks for superuser access
def getTime():
    return datetime.now(tz=pytz.timezone('Asia/Kolkata'))+timedelta(hours=5, minutes=30)
    
def authenticate(request, phone_number = None, password = None):
    
    try:
        user = storeData.objects.get(phone_number = phone_number)
    except:
        print(phone_number)
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

# Log out the user on button click
def logout(request):
    userId = request.session.get('user_info')
    print(userId)
    user = storeData.objects.get(id = userId)
    user.is_logged_in = False
    user.save()
    request.session['user_info'] = -1
    return redirect('home')


# Function to update the attendance of the students
def markPresent(present):
    print(getTime())
    for id in present:
        person = storeData.objects.get(id = id)
        person.last_class_attended = getTime()
        person.no_of_class_attended += 1
        person.save()

   
    last_month = person.last_class_attended.strftime("%m")
    if last_month != storeData.objects.get(is_superuser = 1).last_class_attended.strftime("%m"):
        for user in storeData.objects.all():
            if user.is_superuser:
                user.last_class_attended = getTime()
            elif user.id in present:
                user.no_of_class_attended = 1
            else:
                user.no_of_class_attended = 0
            
            user.save()


# Save a Message entry from both students and the admin(s)
def sendMessage(request, message, recipients):
    receivers = []
    
    for user in recipients:
        receivers.append(user['username'])
        name = storeData.objects.get(username = user['username'])
        name.unseen_message_count += 1
        name.save()

    userId = request.session.get('user_info')
    sender = storeData.objects.get(id = userId)

    message = Message(message = message, allowedUsers = repr(receivers), sender = sender.username, datePosted = getTime())
    message.save()

def upload(recipients):
    receivers = []

    for user in recipients:
        receivers.append(user['username'])
        name = storeData.objects.get(username = user['username'])
        name.unseen_file_count += 1
        name.save()

    newFile = FileUpload.objects.all()[len(FileUpload.objects.all())-1]    
    newFile.allowedUsers = receivers
    newFile.save()

def checkStatus(request, sudo = False):
    userId = request.session.get('user_info')
    try:
        user = storeData.objects.get(id = userId)
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

def errorMessage(request, errorCode = None):
    if errorCode == 'notSignedIn':
        messages.info(request, "You have logged out. Please login again to access content")
        return redirect('home')
    
    elif errorCode == 'notValidated':
        messages.info(request, 'Looks like the teacher has not approved of your account yet. Please try again later or contact the teacher.')

    elif errorCode == 'accountExists':
        messages.info(request, 'Looks like there is an account with these credentials already.')
        return redirect('login')
    
    elif errorCode == 'wrongPassword':
        messages.info(request, 'Please enter the correct password')

def download(id):

    file_name = FileUpload.objects.get(id = id).uploadedFile.url
    file_path = settings.MEDIA_ROOT + file_name
    
    content_type = None
    extension = os.path.splitext(file_name)[1][1:]
    if extension == 'png':
        content_type = 'image/png'
    elif extension == 'jpg':
        content_type = 'image/jpg'
    elif extension == 'jpeg':
        content_type = 'image/jpeg'
    elif extension == 'pdf':
        content_type = 'application/pdf'

    print(file_path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type=content_type )
            response['Content-Disposition'] = 'attachment; filename='+os.path.basename(file_path)
            return response

    raise Http404

def deleteOldMessage(messages):
    for message in messages:
        print(message.message)
        message.delete()
    
def deleteOldFiles(files):
    for file_name in files:
        file_path = settings.MEDIA_ROOT + file_name.uploadedFile.url
        if os.path.exists(file_path):
            os.remove(file_path)
        
        file_name.delete()

def recoverPassword(request):
    if request.method == 'POST':
        form = phoneNumber(request.POST)
        phone_number = request.POST.get('phone_number')
        try:
            user = storeData.objects.get(phone_number = phone_number)
            sendMail(user)
            messages.info(request, 'Details sent to your accout mail')
            return render(request, 'home.html')
        except:
            messages.info('This phone number is not present. Check out with other phone numbers that you may have used')
    else:
        form = phoneNumber()
    return render(request, 'Registry/recover.html', {'form': form})

def sendMail(user):
    subject = str(user.username) + " details."
    body = "User password : " + str(user.password)
    sender = 'Vidya.carnatic.music@gmail.com'
    receiver = user.email_address
    send_mail(subject, body, sender, [receiver, ])

def deleteUser(request):
    if request.method == 'POST':
        if 'delete' in request.POST:
            form = delete_form(request.POST)
            selected_users = []
            for user in storeData.objects.values():
                    if request.POST.get(str(user['id'])):
                        student = storeData.objects.get(username = user['username'])
                        print(student.username)
                        student.delete()
            messages.info(request, 'Selected users deleted.')
            return HttpResponseRedirect('/admin-home/')
        if 'search' in request.POST:
            search = request.POST.get("search_field")
            similar_users = storeData.objects.filter(username__icontains=search) 
            LIST_OF_CHOICES_1 = []
            LIST_OF_CHOICES_2 = []

            for user in similar_users:
                if not user.is_superuser and user.validated:
                    if user.batch_number == 1:
                        LIST_OF_CHOICES_1.append({'name': user.username, 'id': user.id}) 
                    else:
                        LIST_OF_CHOICES_2.append({'name': user.username, 'id': user.id})

            form = delete_form()
            args = {'form': form,'students': {"batch1": LIST_OF_CHOICES_1, "batch2": LIST_OF_CHOICES_2}}

            return render(request, 'Registry/deleteUser.html', args)
    else:
        LIST_OF_CHOICES_1 = []
        LIST_OF_CHOICES_2 = []
        for user in storeData.objects.values():
            if not user['is_superuser'] and user['validated']:
                if user['batch_number'] == 1:
                    LIST_OF_CHOICES_1.append({'name': user['username'], 'id': user['id']}) 
                else:
                    LIST_OF_CHOICES_2.append({'name': user['username'], 'id': user['id']})

        form = delete_form()
        args = {'form': form,'students': {"batch1": LIST_OF_CHOICES_1, "batch2": LIST_OF_CHOICES_2}}

        return render(request, 'Registry/deleteUser.html', args)