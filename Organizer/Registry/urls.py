from django.urls import path
from . import views

urlpatterns = [
        path('', views.home, name='home'),
        path('login/', views.login, name = 'login'),
        path('signup/', views.register, name = 'signup'),
        path('admin-home/', views.loginAdminHome, name = 'adminhome'),
        path('student-home/', views.loginStudentHome, name = 'studenthome'),
        path('admin-home/student-data/', views.studentsData, name = 'studentsData'),
        path('admin-home/attendance/', views.attendance, name = 'attendance'),
        path('admin-home/fees/', views.fees, name = 'fees'),
        path('admin-home/admin-message/', views.adminViewMessage, name = 'adminViewMessage'),
        path('admin-home/admin-message/send/', views.adminSendMessage, name = 'adminSendMessage'),
        path('admin-home/validate/', views.validateStudent, name = 'validateStudent'),
        path('student-home/student-message/', views.studentViewMessage, name = 'studentViewMessage'),
        path('admin-home/admin-upload-files/', views.uploadFile, name = 'uploadFile'),
        path('student-home/student-message/send/',  views.studentSendMessage, name = 'studentSendMessage'),
        path('student-home/student-download-files/', views.downloadFile, name = 'downloadFile'),
        path('logout/', views.logout, name="logout"),
]