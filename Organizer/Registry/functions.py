from .models import storeData
def uploadFile(recipients):
    receivers = []

    for user in recipients:
        receivers.append(user['username'])
        name = storeData.objects.get(username = user['username'])
        name.unseen_file_count += 1
        name.save()

    newFile = FileUpload.objects.all()[len(FileUpload.objects.all())-1]    
    newFile.allowedUsers = receivers
    newFile.save()


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


def checkStatus(request):
    userId = request.session.get('user_info')
    if userId is not None and userId is not -1:
        return True
    else:
        return False

# Function to update the attendance of the students
def markPresent(present):
    for id in present:
        person = storeData.objects.get(id = id)
        person.last_class_attended = datetime.now()
        person.no_of_class_attended += 1
        person.save()




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
