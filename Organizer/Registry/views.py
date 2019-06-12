from django.shortcuts import render, HttpResponseRedirect, redirect
from .forms import *
from datetime import datetime
from .models import Message, storeData, FileUpload
from django.contrib import messages
import uuid



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
            addr = uuid.getnode()
            Batch = request.POST.get('Batch')
            try:
                user = storeData.objects.get(mac_address = addr)
                messages.info(request, 'Looks like you have already registered with this device')
                
                return HttpResponseRedirect('/')
            
            except:
                newUser = storeData(username = username, password = password, phone_number = phone, mac_address = addr, batch_number = Batch)
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
    
    args = {'requiresValidation': appearance}
    return render(request, 'Registry/adminBase.html', args)


#The home page for the students.
def loginStudentHome(request):

    if checkStatus(request) != -1:

        userData = {'id': None, 'name': '', 'classesAttended': None, 'lastAttended': None, 'feesStatus': False}
        try:
            user_id = request.session.get('user_info')
            user = storeData.objects.get(id = user_id)  
            userData['id'] = user.id
            userData['name'] = user.username
            userData['classesAttended'] = user.no_of_class_attended
            userData['lastAttended'] = user.last_class_attended.date()
            userData['feesStatus'] = user.last_fees_paid.date()
            return render(request, 'Registry/studentBase.html', userData)
        except:
            messages.info(request, "Please login before trying to access student info")
            return redirect('home')
    messages.info(request, "You have logged out. Please login again to access content")
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
    addr = uuid.getnode()
    user = storeData.objects.get(is_superuser = 1)
    id = 0
    for message in Message.objects.values():
        
        if str(user.username) in (message['allowedUsers']):
            
            if message['sender'] == str(user.username):
                names = ""

                for name in eval(message['allowedUsers']):
                    names += name + ', ' 
                
                names = names[:len(names)-1]
                final['sent'].append({'id': str(id), 'brief': message['message'][:10]+"...", 'posts': message['message'], 'dates': str(message['datePosted'].date()), 'receivers': names})
            else:
                final['received'].append({'id': str(id), 'brief': message['message'][:10]+"...",  'posts': message['message'], 'dates': str(message['datePosted'].date()), 'sender': str(message['sender'])})
            
            id += 1
          
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
                recipients = storeData.objects.values()

            elif request.POST.get('batch1'):
                for user in storeData.objects.values():
                    if user['batch_number'] == 1:
                        recipients.append(user)
            
            elif request.POST.get('batch2'):
                for user in storeData.objects.values():
                    if user['batch_number'] == 2:
                        recipients.append(user)

            else:
                for user in storeData.objects.values():
                    if request.POST.get(str(user['id'])):
                        recipients.append(user)
            
            # Function to save the the message to the database
            sendMessage(message, recipients)
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
                recipients = storeData.objects.values()

            elif request.POST.get('batch1'):
                for user in storeData.objects.values():
                    if user['batch_number'] == 1:
                        recipients.append(user)
            
            elif request.POST.get('batch2'):
                for user in storeData.objects.values():
                    if user['batch_number'] == 2:
                        recipients.append(user)

            else:
                for user in storeData.objects.values():
                    if request.POST.get(str(user['id'])):
                        recipients.append(user)
            
            upload(recipients)
            messages.info(request, 'File has been uploaded.')
            
            return redirect('adminhome')
    else:
        form = FileUploadForm()
        LIST_OF_CHOICES = []

        for user in storeData.objects.values():
            if not user['is_superuser']:
                LIST_OF_CHOICES.append(user)

        args = {"form": form, "students": LIST_OF_CHOICES}
        #args = {"form": form}

    return render(request, 'Registry/uploadFile.html', args)

# Function for the student to send message to the teacher/superusers
def studentSendMessage(request):
    
    args = {}
    
    if request.method == 'POST':
    
        form = SelectStudentForm(request.POST)
    
        if form.is_valid:
    
            message = request.POST['message']

            for user in storeData.objects.values():
                if user['is_superuser'] == True:
                    admin = user
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
    

# A function for the students to see the messages sent by the admin
def studentViewMessage(request):
    final = {'message': []}

    addr = uuid.getnode()
    #user = storeData.objects.get(mac_address = addr)
    userId = request.session.get('user_info')
    user = storeData.objects.get(id = userId)
    for message in Message.objects.values():

        if str(user.username) in (message['allowedUsers']):
            final['message'].append({'posts': message['message'], 'dates': str(message['datePosted'].date()) })
    
    return render(request, 'Registry/studentViewMessage.html', final)

def downloadFile(request):
    return render(request, 'Registry/downloadFile.html')

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
            messages.info(request, 'Please enter the correct password')
        else:
            messages.info(request, 'Looks like the admin has not authorised your account. Please try later')
        return "None"
    
    if user.is_superuser == True:
        return "Yes"
    else:
        return "No"

    return "None"


# Log out the user on button click
def logout(request):
    userId = request.session.get('user_info')
    user = storeData.objects.get(id = userId)
    user.is_logged_in = False
    user.save()
    print('here')
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
    userId = request.session.get('user_info')
    sender = storeData.objects.get(id = userId)
    message = Message(message = message, allowedUsers = repr(receivers), sender = sender.username)
    
    message.save()

def upload(recipients):
    #pass
    receivers = []

    for user in recipients:
        receivers.append(user['username'])

    newFile = FileUpload.objects.all()[len(FileUpload.objects.all())-1]    
    newFile.allowedUsers = receivers
    newFile.save()

def checkStatus(request):
    userId = request.session.get('user_info')
    return userId