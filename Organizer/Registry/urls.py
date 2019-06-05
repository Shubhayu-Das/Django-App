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
        path('student-home/student-message/', views.studentMessage, name = 'studentMessage'),
        path('admin-home/admin-message/', views.adminMessage, name = 'adminMessage'),
        path('admin-home/admin-upload-files/', views.uploadFile, name = 'uploadFile'),
        path('admin-home/fees/', views.fees, name = 'fees'),
        path('signup/', views.register, name='signup'),
]
