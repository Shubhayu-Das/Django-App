from django.urls import path
from . import views

urlpatterns = [
        path('', views.home_view, name='home'),
        path('login/', views.login_view, name = 'login'),
        path('signup/', views.register_view, name = 'signup'),
        path('admin-home/', views.login_admin_home_view, name = 'adminhome'),
        path('student-home/', views.login_student_home_view, name = 'studenthome'),
        path('admin-home/student-data/', views.student_data_view, name = 'studentsData'),
        path('admin-home/attendance/', views.attendance_view, name = 'attendance'),
        path('admin-home/fees/', views.fees_view, name = 'fees'),
        path('admin-home/admin-message/', views.admin_view_message_view, name = 'adminViewMessage'),
        path('admin-home/admin-message/send/', views.admin_send_message_view, name = 'adminSendMessage'),
        path('admin-home/delete/', views.delete_user_view, name = 'deleteUser'),
        path('admin-home/validate/', views.validate_student_view, name = 'validateStudent'),
        path('student-home/student-message/', views.student_view_message_view, name = 'studentViewMessage'),
        path('admin-home/admin-view-files/', views.admin_view_file_view, name= 'adminViewFile'),
        path('admin-home/admin-upload-files/', views.admin_upload_file_view, name = 'adminUploadFile'),
        path('student-home/student-message/send/',  views.student_send_message_view, name = 'studentSendMessage'),
        path('student-home/student-download-files/', views.student_download_file_view, name = 'downloadFile'),
        path('recover/', views.recover_password_view, name = 'recoverPassword'),
        path('logout/', views.logout_view, name="logout"),
]