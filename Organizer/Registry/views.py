from .forms import *
from .models import Message, UserData, UploadedFile
import os
from django.contrib import messages
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.conf import settings
from django.http import HttpResponse, Http404
from datetime import datetime, timedelta

import pytz

from .supporters import *

# The base home page which leads to login/sign up pages
def home_view(request):
    try:
        userId = request.session.get('user_info')
        user = UserData.objects.get(id=userId)

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
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            phone_number = request.POST.get('phone_number')
            password = request.POST.get('password')

            response = authenticate(request, phone_number=phone_number, password=password)

            if response == 'Yes':         
                user = UserData.objects.get(phone_number = phone_number)
                request.session['user_info'] = user.id
                if datetime.now().strftime('%m') != request.session.get('last_login'):
                    for user in UserData.objects.all():
                        user.no_of_class_attended = 0
                        user.save()

                request.session['last_login'] = datetime.now().month
                return redirect('/admin-home/')

            elif response == "No":
                user = UserData.objects.get(phone_number = phone_number)
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
def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            phone = request.POST.get('phone_number')
            Batch = request.POST.get('Batch')
            confirm_password = request.POST.get('confirm_password')
            email_address = request.POST.get('email_address')
            if password == confirm_password:
                if len(UserData.objects.filter(phone_number=phone)) != 0:
                    errorMessage(request, 'accountExists')
                    return HttpResponseRedirect('/')

                else:
                    newUser = UserData(username=username, password=password, phone_number=phone, batch_number=Batch,
                                        email_address=email_address)
                    newUser.save()
                    messages.info(request,
                                  'Your registration is complete. Please wait for the administrator to validate your account')
                    return HttpResponseRedirect('/')

            else:
                messages.info(request, "Password confirmation incorrect")
                return HttpResponseRedirect('/')

    else:
        form = RegistrationForm()

    args = {'form': form}

    return render(request, 'Registry/signup.html', args)


# Leads to the home page for the admin, where all the attendance, fees and other activities are there
def login_admin_home_view(request):
    if checkStatus(request, sudo=True) == "superuser":
        appearance = False
        # deleteOldFiles()

        if UserData.objects.filter(validated=0):
            appearance = True

        user = UserData.objects.get(id=request.session.get('user_info'))
        args = {'requiresValidation': appearance, 'messagesUnseen': user.unseen_message_count,
                'total': user.unseen_message_count + user.unseen_file_count}
        return render(request, 'Registry/adminBase.html', args)
    else:
        errorMessage(request, 'notSignedIn')
        return redirect('login')


# The home page for the students.
def login_student_home_view(request):
    if checkStatus(request):
        user_id = request.session.get('user_info')
        user = UserData.objects.get(id=user_id)
        print(user)
        args = {}
        args['id'] = user.id
        args['name'] = user.username
        args['classesAttended'] = user.no_of_class_attended
        args['lastAttended'] = user.last_class_attended.date()
        args['feesStatus'] = user.last_fees_paid.date()
        args['messagesUnseen'] = user.unseen_message_count
        args['filesUnseen'] = user.unseen_file_count
        args['total'] = user.unseen_file_count + user.unseen_message_count

        return render(request, 'Registry/studentBase.html', args)
       
    errorMessage(request, 'notSignedIn')
    return redirect('home')


# Show basic data like the email id and the phone number details(Admin page)
def student_data_view(request):
    if checkStatus(request, sudo = True) == "superuser":
        return render(request, 'Registry/studentsData.html', findStudent(view='student-data'))
    else:
        errorMessage(request, 'notSignedIn')
        return redirect('home')


# Mark and store the attendance functionalities(Admin page)
def attendance_view(request):
    userList = []
    if checkStatus(request, sudo = True) == "superuser":
        args = {}

        if request.method == 'POST':
            if 'attendance' in request.POST:
                present = []
                form = AttendanceForm(request.POST)

                if form.is_valid:
                    for user in UserData.objects.all():
                        if request.POST.get(str(user.id)):
                            present.append(user.id)

                    markPresent(present)
                    messages.info(request, "Attendance has been marked")
                    return redirect('studentsData')

            if 'search' in request.POST:
                userList = findStudent(name=request.POST.get("search_field"), view='attendance')

        else:
            userList = findStudent(view='attendance')

        form = AttendanceForm()
        args = {'form': form ,'students': userList}

        return render(request, 'Registry/attendance.html', args)
    else:
        errorMessage(request, 'notSignedIn')
        return redirect('home')


# The last fees paid date
def fees_view(request):
    userList = []
    if checkStatus(request, sudo = True) == "superuser":
        if request.method == 'POST':
            if 'fees' in request.POST:
                form = AttendanceForm(request.POST)

                if form.is_valid:
                    for User in UserData.objects.all():
                        if request.POST.get(str(User.id)):
                            User.last_fees_paid = getTime()
                            User.save()

                    messages.info(request, "Fees details updated")
                    return redirect('fees')

            if 'search' in request.POST:
                userList = findStudent(name=request.POST.get("search_field"), view='fees')
                
        else:
            userList = findStudent(view='fees')

        form = AttendanceForm()
        args = {'form': form ,'students': userList}

        return render(request, 'Registry/fees.html', args)
    else:
        errorMessage(request, 'notSignedIn')
        return redirect('home')


def validate_student_view(request):
    if checkStatus(request, sudo=True) == "superuser":
        if request.method == 'POST':
            form = ValidationForm(request.POST)
            if form.is_valid:
                for student in UserData.objects.all():
                    response = request.POST.get(str(student.id))
                    if (response == "Accept"):
                        student.validated = True
                        student.save()
                    elif (response == "Delete"):
                        student.delete()

                messages.info(request, "Selected students have been validated/deleted accordingly.")
                return redirect('adminhome')
        else:
            form = ValidationForm()
            users = findStudent(view='validate')
            
        return render(request, 'Registry/validate.html', {'users': users})
    else:
        errorMessage(request, 'notSignedIn')
        return redirect('home')


def admin_view_message_view(request):
    if checkStatus(request, sudo=True) == "superuser":
        final = {'received': [], 'sent': []}
        user = UserData.objects.get(is_superuser=1)
        user.unseen_message_count = 0
        user.save()

        displayThreshold = getTime() - timedelta(weeks=1)
        new_message = Message.objects.filter(datePosted__gte=displayThreshold, sender = user)

        deleteOldMessages()

        for message in new_message:
            receivers = message.allowedUsers.all()

            if UserData.objects.filter(is_superuser=0) == receivers:
                receivers = "All students"
            elif UserData.objects.filter(is_superuser=0, batch_number=1) == receivers:
                receivers = "Batch #1 only"
            elif UserData.objects.filter(is_superuser=0, batch_number=2) == receivers:
                receivers = "Batch #2 only"
            else:
                receivers = ", ".join(map(lambda x: x.username, receivers))
            
            final['sent'].append({'id': message.id, 'brief': message.message[:10]+"...", 'posts': message.message, 'dates': str(message.datePosted.date()), 'receivers': receivers})

        for message in Message.objects.filter(allowedUsers__is_superuser=True):
            final['received'].append(
                {'id': message.id, 'brief': message.message[:10] + "...", 'posts': message.message,
                    'dates': str(message.datePosted.date()), 'sender': message.sender})

        return render(request, 'Registry/adminViewMessage.html', final)
    else:
        errorMessage(request, 'notSignedIn')
        return redirect('home')


# View for message broadcasting
def admin_send_message_view(request):
    if checkStatus(request, sudo=True):
        args = {}
        if request.method == 'POST':
            if 'send' in request.POST:
                recipients = []
                form = SelectStudentForm(request.POST)

                if form.is_valid:
                    message = request.POST['message']

                    if 'selectall' in request.POST:
                        recipients = UserData.objects.filter(is_superuser = 0)

                    elif 'batch1' in request.POST or 'batch2' in request.POST:
                        recipients = UserData.objects.filter(batch_number = 1 if 'batch1' in request.POST else 2)

                    else:
                        for user in UserData.objects.all():
                            if request.POST.get(str(user.id)):
                                recipients.append(user)

                    # Function to save the the message to the database
                    sendMessage(request.session.get('user_info'), message, recipients)
                    messages.info(request, 'Message has been sent.')

                    return redirect('adminhome')
                    
            if 'search' in request.POST:
                form = SelectStudentForm()
                LIST_OF_CHOICES = findStudent(name=request.POST.get("search_field"), view='findall')
        
                args = {"form": form, "students": LIST_OF_CHOICES}

                return render(request, 'Registry/adminSendMessage.html', args)
        else:
            form = SelectStudentForm()
            LIST_OF_CHOICES = findStudent(view = 'findall')
            print(LIST_OF_CHOICES)
            args = {"form": form, "students": LIST_OF_CHOICES}

        return render(request, 'Registry/adminSendMessage.html', args)
    else:
        errorMessage(request, 'notSignedIn')
        return redirect('home')

# View for the admin to see the list of uploaded files and download them
def admin_view_file_view(request):
    if checkStatus(request, sudo=True) == "superuser":
        args = {}
        userId = request.session.get('user_info')
        user = UserData.objects.get(id=userId)
        if request.method == 'POST':
            form = FileDownloadForm(request.POST)

            if form.is_valid():
                name = str(request.POST.get('fileField'))
                return download(name)

        else:
            args["Files"] = list(map(lambda File: {
                "name": File.fileName, 
                "date": str(File.upload_time.date()),
                'description': File.description
                }, \
                UploadedFile.objects.all()))
            return render(request, 'Registry/adminViewFile.html', args)

    else:
        errorMessage(request, 'notSignedIn')
        return redirect('home')


# Function to upload files to the system
def admin_upload_file_view(request):
    if checkStatus(request, sudo=True) == "superuser":
        args = {}

        if request.method == 'POST':
            if 'upload' in request.POST:
                recipients = []
                form = UploadedFileForm(request.POST, request.FILES)
                
                if form.is_valid():
                    if request.POST.get('selectall'):
                        recipients = UserData.objects.filter(is_superuser=0)

                    elif request.POST.get('batch1'):
                        recipients = UserData.objects.filter(batch_number=1)

                    elif request.POST.get('batch2'):
                        recipients = UserData.objects.filter(batch_number=2)

                    else:
                        for user in UserData.objects.all():
                            if request.POST.get(str(user.id)):
                                recipients.append(user)

                    upload(request.POST['file_description'], recipients, request.FILES['upload_file'])
                    messages.info(request, 'File has been uploaded.')
                    return redirect('adminhome')
                else:
                    return redirect('adminUploadFile')

            if 'search' in request.POST:
                form = UploadedFileForm()
                LIST_OF_CHOICES = []
                search = request.POST.get("search_field")
                similar_users = UserData.objects.filter(username__icontains=search)
                for user in similar_users:
                    if not user.is_superuser:
                        LIST_OF_CHOICES.append(user)

                args = {"form": form, "students": LIST_OF_CHOICES}
                return render(request, 'Registry/adminUploadFile.html', args)
        else:
            form = UploadedFileForm()
            LIST_OF_CHOICES = []

            for user in UserData.objects.values():
                if not user['is_superuser']:
                    LIST_OF_CHOICES.append(user)

            args = {"form": form, "students": LIST_OF_CHOICES}
            return render(request, 'Registry/adminUploadFile.html', args)
    else:
        errorMessage(request, 'notSignedIn')
        return redirect('home')


# Function for the student to send message to the teacher/superusers
def student_send_message_view(request):
    if checkStatus(request):
        args = {}

        if request.method == 'POST':
            form = SelectStudentForm(request.POST)
            if form.is_valid:

                message = request.POST['message']
                admin = UserData.objects.filter(is_superuser = 1)

                # invoke the message sending function
                sendMessage(request.session.get('user_info'), message, list(admin))
                messages.info(request, 'Message has been sent.')

                return redirect('/student-home')
        else:
            form = SelectStudentForm()
            args = {"form": form}
        return render(request, 'Registry/studentSendMessage.html', args)

    errorMessage(request, 'notSignedIn')
    return redirect('home')


# A function for the students to see the messages sent by the admin
def student_view_message_view(request):
    if checkStatus(request):
        try:
            userId = request.session.get('user_info')
            user = UserData.objects.get(id=userId)

            user.unseen_message_count = 0
            user.save()

            final = {'received': [], 'sent': []}
            
            final['sent'].append(list(map(lambda message: {
                'id': message.id,
                'brief': message.message[:10] + "...", 'posts': message.message,
                'dates': str(message.datePosted.date())}, \
                Message.objects.filter(sender=user)[:3])))
            
            final['sent'].append(list(map(lambda message: {
                'id': message.id,
                'brief': message.message[:10] + "...",
                'posts': message.message,
                'dates': str(message.datePosted.date())}, \
                Message.objects.filter(allowedUsers__id=user.id)[:3])))

            return render(request, 'Registry/studentViewMessage.html', final)
        except:
            errorMessage(request, 'notSignedIn')
            return redirect('home')

    errorMessage(request, 'notSignedIn')
    return redirect('home')

# Function to allow students to download the files that have been uploaded for them
def student_download_file_view(request):
    if checkStatus(request):
        args = {"Files": []}
        userId = request.session.get('user_info')
        user = UserData.objects.get(id=userId)
        user.unseen_file_count = 0
        user.save()
    
        if request.method == 'POST':
            form = FileDownloadForm(request.POST)

            if form.is_valid():
                name = str(request.POST.get('fileField'))
                return download(name)
        else:
            for File in UploadedFile.objects.filter(allowedUsers__id=userId):
                args["Files"].append({"name": File.fileName, 
                                "date": str(File.upload_time.date()), 'description': File.file_description})

            return render(request, 'Registry/downloadFile.html', args)

    else:
        errorMessage(request, 'notSignedIn')
        return redirect('home')

# Log out the user on button click
def logout_view(request):
    userId = request.session.get('user_info')
    user = UserData.objects.get(id=userId)
    user.is_logged_in = False
    user.save()

    request.session['user_info'] = -1
    return redirect('home')


# Function to send an email when forgot password option is selected
def recover_password_view(request):
    if request.method == 'POST':
        form = PhoneNumber(request.POST)
        phone_number = request.POST.get('phone_number')
        try:
            user = UserData.objects.get(phone_number=phone_number)
            sendMail(user)
            messages.info(request, 'Details sent to your accout mail')
            return redirect('login')
        except:
            messages.info(request, 'This phone number is not present. Check out with other phone numbers that you may have used')

        return redirect('home')
    else:
        form = PhoneNumber()
    return render(request, 'Registry/recover.html', {'form': form})

# Function to delete an user, accessed by the admin
def delete_user_view(request):
    if request.method == 'POST':
        if 'delete' in request.POST:
            form = DeleteStudentForm(request.POST)
            selected_user_ids = list(filter(lambda x: int(x) if str.isdigit(x) else None, request.POST.keys()))
            
            for id in selected_user_ids:
                student = UserData.objects.get(id=id)
                student.validated = False
                student.save()

            messages.info(request, 'Selected users have been invalidated.')
            return HttpResponseRedirect('/admin-home/')

        if 'search' in request.POST:

            form = DeleteStudentForm()
            args = {'form': form, 'students': findStudent(request.POST.get("search_field"), view='delete')}
            return render(request, 'Registry/deleteUser.html', args)

        if 'change' in request.POST:
            form = DeleteStudentForm(request.POST)
            selected_user_ids = list(filter(lambda x: int(x) if str.isdigit(x) else None, request.POST.keys()))
            
            for id in selected_user_ids:
                student = UserData.objects.get(id=id)
                student.batch_number = 3 - student.batch_number
                student.save()

            messages.info(request, 'Batch number of selected users has been changed.')
            return HttpResponseRedirect('/admin-home/')
    else:
        form = DeleteStudentForm()
        args = {'form': form, 'students': findStudent(view='delete')}

        return render(request, 'Registry/deleteUser.html', args)