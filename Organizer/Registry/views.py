from django.shortcuts import render, HttpResponseRedirect, redirect
from .forms import LoginForm, SelectStudentForm, RegistrationForm, AttendanceForm, FileUploadForm
from datetime import datetime
from .models import Message, storeData
from django.contrib import messages
import uuid


def systemCheck():
    addr = uuid.getnode()
    user = user = storeData.objects.get(mac_address = addr)
    if user.is_logged_in == True:
        return 1
    else:
        return 0



def authenticate(request, username = None, password = None):
    
    user = storeData.objects.get(username = username)
    
    if password == user.password and user.validated == True:
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

def userlogout(username):
    user = storeData.objects.get(username = username)
    user.is_logged_in = False
    user.save()
    
    return True


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
            print(response)
            if response == 'Yes':         
                return redirect('/admin-home/')
            elif response == "No":
                user = storeData.objects.get(username = username)
                messages.info(request, str(user.id))
                request.session['user_info'] = user.id
                return redirect('/student-home/')
            else:
                return redirect('/home/')
        
        else:
            print(form.errors)
    else:
        form = LoginForm()
    return render(request, 'Registry/login.html', {"form": form})

def register(request):
    if request.method =='POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            phone = request.POST.get('phone_number')
            addr = uuid.getnode()
            try:
                user = storeData.objects.get(mac_address = addr)
                messages.info(request, 'Looks like you have already registered with this device')
                return HttpResponseRedirect('/home/')
            except:
                storeData.objects.create(username = username, password = password, phone_number = phone, mac_address = uuid.getnode())
                messages.info(request, 'Your registration is complete. Please wait for the administrator to validate your account')
                return HttpResponseRedirect('/home/')
    else:
        form = RegistrationForm()
    args = {'form': form}
    return render(request, 'Registry/signup.html', args)


# Leads to the home page for the admin, where all the attendance, fees and other activities are there
def loginAdminHome(request):
    return render(request, 'Registry/adminBase.html')

# The last fees paid date
def fees(request):
    return render(request, 'Registry/fees.html')

# Show basic data like the email id and the phone number details(Admin page)
def studentsData(request):

    args = {'users':[]}
    for user in storeData.objects.values():
        if not user['is_superuser']:
            temp = {'id': None, 'name': '', 'phoneNumber': '', 'classesAttended': None, 'lastAttended': None, 'feesStatus': False, 'isValidated': False}
            temp['id'] = (user['id'])
            temp['name'] = (user['username'])
            temp['phoneNumber'] = (user['phone_number'])
            temp['classesAttended'] = (user['no_of_class_attended'])
            temp['lastAttended'] = (user['last_class_attended'].date())
            temp['feesStatus'] = (user['fee_status'])
            temp['isValidated'] = (user['validated'])

            args['users'].append(temp)
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
        LIST_OF_CHOICES = []
        form = AttendanceForm()
        for user in storeData.objects.values():
            if not user['is_superuser']:
                LIST_OF_CHOICES.append({'name': user['username'], 'id': user['id'], 'number': user['no_of_class_attended'], 'lastAttended': user['last_class_attended'].date()})

        args = {'form': form ,'students': LIST_OF_CHOICES}

    return render(request, 'Registry/attendance.html', args)

# View for message broadcasting
def admin_Send_Message(request):

    args = {}
    if request.method == 'POST':
        recipients = []
        form = SelectStudentForm(request.POST)
        if form.is_valid:
            message = request.POST['message']
            if request.POST.get('selectall'):
                recipients = storeData.objects.values()
            else:
                for user in storeData.objects.values():
                    if request.POST.get(str(user['id'])):
                        recipients.append(user)

            sendMessage(message, recipients)
            messages.info(request, 'Message has been sent.')
            return redirect('adminhome')
        
    else:
        form = SelectStudentForm()
        LIST_OF_CHOICES = []

        for user in storeData.objects.values():
            if not user['is_superuser']:
                LIST_OF_CHOICES.append(user)

        args = {"form": form, "students": LIST_OF_CHOICES}

    return render(request, 'Registry/adminMessage.html', args)
def student_Send_Message(request):
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
            print("Sent message")
            sendMessage(message, l)
            return redirect('/student-home')
    else:
            form = SelectStudentForm()
            args = {"form": form}
    return render(request, 'Registry/student_Send_Message.html', args)
def uploadFile(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('adminhome')
    else:
        form = FileUploadForm()

    return render(request, 'Registry/uploadFile.html', {'form': form})

def markPresent(present):
    for id in present:
        person = storeData.objects.get(id = id)
        person.last_class_attended = datetime.now()
        person.no_of_class_attended += 1
        person.save()

def sendMessage(message, recipients):
    receivers = []
    for user in recipients:
        receivers.append(user['username'])
    sender = storeData.objects.get(mac_address = uuid.getnode())
    message = Message(message = message, allowedUsers = repr(receivers), sender = sender.username)
    message.save()
    

#The home page for the students.
def loginStudentHome(request):
    if (systemCheck()):
        user_id = request.session.get('user_info')
        user = storeData.objects.get(id = user_id)
        user_data = {'id': None, 'name': '', 'classesAttended': None, 'lastAttended': None, 'feesStatus': False}
        user_data['id'] = user.id
        user_data['name'] = user.username
        user_data['classesAttended'] = user.no_of_class_attended
        user_data['lastAttended'] = user.last_class_attended.date()
        user_data['feesStatus'] = user.fee_status
        return render(request, 'Registry/studentBase.html', user_data)
    messages.info(request, "Please login before trying to access user information")
    return HttpResponseRedirect('/home/')

def admin_View_Message(request):
    final = {'message': []}
    addr = uuid.getnode()
    user = storeData.objects.get(is_superuser = 1)
    for message in Message.objects.values():
        #print(message['allowedUsers'])
        print(message)
        if str(user.username) in (message['allowedUsers']):
            print(message['allowedUsers'])
            print(user.username)
            print("Yes")
            print(message['message'])
            final['message'].append({'posts': (message['message']), 'dates': (str(message['datePosted'])), 'sender': (str(message['sender']))})
    print(final)
    return render(request, 'Registry/admin_View_Message.html', final)

def student_View_Message(request):
    final = {'message': []}
    addr = uuid.getnode()
    user = storeData.objects.get(mac_address = addr)
    for message in Message.objects.values():
        print(message['allowedUsers'])
        if str(user.username) in (message['allowedUsers']):
            final['message'].append({'posts': (message['message']), 'dates': (str(message['datePosted'])), 'sender': (str(message['sender']))})
    return render(request, 'Registry/student_View_Message.html', final)


# logout functionality
def logout(request):
    #userlogout(request.user)
    return redirect('home')
    