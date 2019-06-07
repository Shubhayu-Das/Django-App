from django.urls import path
from . import views

urlpatterns = [
        path('', views.home, name='home'),
        path('login/', views.login, name = 'login'),
        path('admin-home/', views.loginAdminHome, name = 'adminhome'),
        path('student-home/', views.loginStudentHome, name = 'studenthome'),
        path('home/', views.logout, name="logout"),
        path('admin-home/attendance/', views.attendance, name = 'attendance'),
        path('admin-home/student-data/', views.studentsData, name = 'studentsData'),
        path('student-home/student-message/', views.student_View_Message, name = 'student_View_Message'),
        path('student-home/student-message/send',  views.student_Send_Message, name = 'student_Send_Message'),
        path('admin-home/admin-message/', views.admin_View_Message, name = 'admin_View_Message'),
        path('admin-home/admin-message/send', views.admin_Send_Message, name = 'admin_Send_Message'),
        path('admin-home/admin-upload-files/', views.uploadFile, name = 'uploadFile'),
        path('admin-home/fees/', views.fees, name = 'fees'),
        path('signup/', views.register, name='signup'),
]
