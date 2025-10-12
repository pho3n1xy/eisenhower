from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Task


#Decorator to protect the matrix view
@login_required
def matrix_view(request):
    """
    This view handles the logic for displaying the main Eisenhower Matrix.
    It fetches all non-archived tasks and categorizes them into the four quadrants.
    """
    # Fetch all tasks that are not archived to display on the main board
    tasks = Task.objects.filter(is_archived=False)

    # Use list comprehensions to efficiently categorize tasks based on their quadrant
    do_first_tasks = [task for task in tasks if task.quadrant == 'do']
    schedule_tasks = [task for task in tasks if task.quadrant == 'schedule']
    delegate_tasks = [task for task in tasks if task.quadrant == 'delegate']
    delete_tasks = [task for task in tasks if task.quadrant == 'delete']

    # The context is a dictionary that maps variable names in the template to Python objects
    context = {
        'do_first_tasks': do_first_tasks,
        'schedule_tasks': schedule_tasks,
        'delegate_tasks': delegate_tasks,
        'delete_tasks': delete_tasks,
    }

    # Render the HTML template with the categorized task data
    return render(request, 'tasks/matrix.html', context)

def login_view(request):
    """
    Handles both displaying the login form and processing the login attempt.
    """
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('tasks:matrix')
        else:
            error = "Invalid username or password. Please try again."

    return render(request, 'tasks/login.html', {'error': error})

def logout_view(request):
    """
    Logs the user out and redirects them to the login page.
    """
    logout(request)
    return redirect('tasks:login')
