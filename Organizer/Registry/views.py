from .forms import *
from .models import Message, storeData, FileUpload
from datetime import datetime
import os
from django.contrib import messages
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.conf import settings
from django.http import HttpResponse, Http404


# The base home page which leads to login/sign up pages
def home(request):          
    return render(request, 'home.html')


# The page to log in. Handles superusers(admins) and normal users(students) separately
def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')

            response = authenticate(request, username=username, password=password)

            if response == 'Yes':         
                user = storeData.objects.get(username = username)
                request.session['user_info'] = user.id
                return redirect('/admin-home/')

            elif response == "No":
                user = storeData.objects.get(username = username)
                messages.info(request, str(user.id))
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
            try:
                user = storeData.objects.get(username = username, phone_number = phone)
                errorMessage(request, 'accountExists')                
            
            except:
                newUser = storeData(username = username, password = password, phone_number = phone, batch_number = Batch)
                newUser.save()
                messages.info(request, 'Your registration is complete. Please wait for the administrator to validate your account')
            
                return HttpResponseRedirect('/')
    
    else:
        form = RegistrationForm()
    
    args = {'form': form}
    
    return render(request, 'Registry/signup.html', args)


# Leads to the home page for the admin, where all the attendance, fees and other activities are there
def loginAdminHome(request):
    appearance = False
    for user in storeData.objects.values():
        if not user['validated']:
            appearance = True

    user = storeData.objects.get(id = request.session.get('user_info'))
    args = {'requiresValidation': appearance, 'messagesUnseen': user.unseen_message_count}
    return render(request, 'Registry/adminBase.html', args)


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

            return render(request, 'Registry/studentBase.html', userData)
        except:
            errorMessage(request, "notSignedIn")
            return redirect('home')
    
    errorMessage(request, 'notSignedIn')
    return redirect('home')

# Show basic data like the email id and the phone number details(Admin page)
def studentsData(request):

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


# Mark and store the attendance functionalities(Admin page)
def attendance(request):

    args = {}

    if request.method == 'POST':
        present = []
        form = AttendanceForm(request.POST)

        if form.is_valid:
            for user in storeData.objects.values():
                if request.POST.get(str(user['id'])):
                    present.append(user['id'])

            markPresent(present)
            return redirect('studentsData')

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


# The last fees paid date
def fees(request):

    args = {}

    if request.method == 'POST':
        present = []
        form = AttendanceForm(request.POST)

        if form.is_valid:
            for user in storeData.objects.values():
                if request.POST.get(str(user['id'])):
                    User = storeData.objects.get(id = str(user['id']))
                    User.last_fees_paid = datetime.now()
                    User.save()
                    
            return redirect('fees')

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

def validateStudent(request):
    if request.method == 'POST':
        form = ValidationForm(request.POST)
        if form.is_valid:
            for user in storeData.objects.values():
                response = request.POST.get(str(user['id']))
                student = storeData.objects.get(id = str(user['id']))
                if(response == "Validate"): 
                    student.validated = True
                    student.save()
                elif(response == "Discard"):
                    student.delete()
            return redirect('home')
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


def adminViewMessage(request):
    final = {'received': [], 'sent': []}
    user = storeData.objects.get(is_superuser = 1)
    user.unseen_message_count = 0
    user.save()
    id = 0
    countRcv = 0
    countSent = 0
    for message in Message.objects.values():

        if countSent < 3:
            if message['sender'] == str(user.username):
                final['sent'].append({'id': str(id), 'brief': message['message'][:10]+"...", 'posts': message['message'], 'dates': str(message['datePosted'].date())})
                countSent += 1
        if countRcv < 3:
           if str(user.username) in (message['allowedUsers']):
                final['received'].append({'id': str(id), 'brief': message['message'][:10]+"...",  'posts': message['message'], 'dates': str(message['datePosted'].date()), 'sender': str(message['sender'])})
                countRcv += 1
        id += 1
        if countRcv == 4 or countSent == 4:
            break

    return render(request, 'Registry/adminViewMessage.html', final)


# View for message broadcasting
def adminSendMessage(request):

    args = {}
    if request.method == 'POST':
        
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
        
    else:
        form = SelectStudentForm()
        LIST_OF_CHOICES = []

        for user in storeData.objects.values():
            if not user['is_superuser'] and user['validated']:
                LIST_OF_CHOICES.append(user)

        args = {"form": form, "students": LIST_OF_CHOICES}

    return render(request, 'Registry/adminSendMessage.html', args)


# Function to upload files to the system
def uploadFile(request):
    
    args = {}

    if request.method == 'POST':
        
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
            return redirect('uploadFile')
    else:
        form = FileUploadForm()
        LIST_OF_CHOICES = []

        for user in storeData.objects.values():
            if not user['is_superuser']:
                LIST_OF_CHOICES.append(user)

        args = {"form": form, "students": LIST_OF_CHOICES}
        print("Here")
        return render(request, 'Registry/uploadFile.html', args)

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
                lst = []
                for File in FileUpload.objects.values():
                    if request.POST.get(str(File['id'])):
                        lst.append(File['id'])
                return download(lst)
        else:
            for File in FileUpload.objects.values():
                if str(user.username) in File['allowedUsers']:
                    args["Files"].append({"id": File["id"], "name": os.path.basename(FileUpload.objects.get(id = File['id']).uploadedFile.path), "date": str(File['upload_time'].date())})

            return render(request, 'Registry/downloadFile.html', args)
    
    else:
        errorMessage(request,  'notSignedIn')
        return redirect('home')

'''------------------------------------------------------------------------------------------------------------------------------------------------'''
''' 
    These are the utility functions which are used above.
    Will have to move these to a separate file later on for proper ordering
    
    Function descriptions:

    The authentication is based on the MAC Address of the user.
    
    fn: authenticate(username, password) --> checks if the User has entered a valid username-password combination

    fn: logout(username) --> Logs out the user onclick

    fn: markPresent(present) --> updates the attendance after taking input from the form

    fn: sendMessage(message, recipients) -->  Saves a message to the Message database
'''

# Function to verify if the password is correct or wrong. Further checks for superuser access
def authenticate(request, username = None, password = None):
    
    try:
        user = storeData.objects.get(username = username)
    except:
        messages.info(request, "Enter valid username")
        return "None"
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
    for id in present:
        person = storeData.objects.get(id = id)
        person.last_class_attended = datetime.now()
        person.no_of_class_attended += 1
        person.save()

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
    message = Message(message = message, allowedUsers = repr(receivers), sender = sender.username)
    
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

def checkStatus(request):
    userId = request.session.get('user_info')
    if userId is not None and userId is not -1:
        return True
    else:
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

def download(ids):
    for id in ids:
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
        #file_path = os.path.join(settings.MEDIA_ROOT, path)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type=content_type )
                response['Content-Disposition'] = 'attachment; filename='+os.path.basename(file_path)
                return response

        raise Http404