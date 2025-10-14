from django.urls import path
from . import views

# This namespace helps avoid URL name collisions with other apps
app_name = 'tasks'

urlpatterns = [
    # When a request comes to the app's root (''), call the matrix_view function
    path('', views.matrix_view, name='matrix'),

    # Route for the new task creation page
    path('create/', views.create_task, name='create'),

    #URL for login page
    path('login/', views.login_view, name='login'), 

    #URL to handle logging out 
    path('logout/', views.logout_view, name='logout'), 

    #URL to handle editing views
    path('edit/<int:pk>/', views.edit_task, name='edit_task')
]

