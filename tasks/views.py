from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Task
from django.http import HttpResponseRedirect
from .forms import TaskForm


#Decorator to protect the matrix view
@login_required
def matrix_view(request):
    """
    This view handles the logic for displaying the main Eisenhower Matrix.
    It fetches all non-archived tasks and categorizes them into the four quadrants.
    """

    tasks = Task.objects.filter(assignee=request.user, is_archived=False)
    
    context = {
        'do_first_tasks': tasks.filter(urgent=True, important=True),
        'schedule_tasks': tasks.filter(urgent=False, important=True),
        'delegate_tasks': tasks.filter(urgent=True, important=False),
        'delete_tasks': tasks.filter(urgent=False, important=False),
    }
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

@login_required
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.requester = request.user
            task.assignee = request.user
            task.save()
            form.save_m2m()
            return redirect('tasks:matrix')
        # If the form is invalid, this 'if' block ends, and the code
        # continues to the final 'return' statement below.
    else:
        # This handles the initial GET request
        form = TaskForm()

    # This line MUST be at the base indentation level of the function.
    # It should NOT be inside the 'else' block.
    return render(request, 'tasks/task_form.html', {'form': form})
        

