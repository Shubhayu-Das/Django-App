from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from .forms import LoginForm, SelectStudentForm, RegistrationForm
from datetime import date
from .models import Message, storeData

def authenticate(username = None, password = None):
    '''
    user = storeData.objects.get(username = username)
    print(user['password'])
    if password == user.password:
        user['is_logged_in'] = True
        user.save()
    else:
        return None
    
    if user.is_superuser == True:
        return "Yes"
    else:
        return "No"
    '''
    return "Yes"

def userlogout(username):
    user = storeData.objects.get(username = username)
    user.is_logged_in = False
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

            response = authenticate(username=username, password=password)
            print(response)
            if response == 'Yes':         
                return redirect('/admin-home/')
            elif response == "No":
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
            storeData.objects.create(username = username, password = password, phone_number = phone)
            
            return redirect('/login/')
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

# Show basic data like the email id and the phone number details.
def studentsData(request):
    return render(request, 'Registry/studentsData.html')

# Mark and store the attendance functionalities
def attendance(request):
    if request.user.is_logged_in:
        return render(request, 'Registry/attendance.html')

# View for message broadcasting
def adminMessage(request):

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
            return redirect('adminhome')
        
    else:
        form = SelectStudentForm()
        LIST_OF_CHOICES = []

        for user in storeData.objects.values():
            if not user['is_superuser']:
                LIST_OF_CHOICES.append(user)

        args = {"form": form, "students": LIST_OF_CHOICES}

    return render(request, 'Registry/adminMessage.html', args)

def sendMessage(message, recipients):
    receivers = []
    for user in recipients:
        receivers.append(user['username'])
    message = Message(message = message, allowedUsers = repr(receivers))
    message.save()
    

#The home page for the students, where they can access the files uploaded
def loginStudentHome(request):
    return render(request, 'Registry/studentBase.html')

def studentMessage(request):
    toView = {'posts': [], 'dates': []}
    print(request.user)
    for message in Message.objects.values():
        if str(request.user) in eval(message['allowedUsers']):
            print("Yes")
            toView['posts'].append(message['message'])
            toView['dates'].append(str(message['datePosted']))

    return render(request, 'Registry/studentMessage.html', toView)

# logout functionality
def logout(request):
    #userlogout(request.user)
    return redirect('home')