from django.shortcuts import render, redirect, get_object_or_404
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


        
@login_required
def edit_task(request, pk):
    # Get the specific task object we want to edit, or return a 404 error if it doesn't exist
    task = get_object_or_404(Task, pk=pk, assignee=request.user)

    if request.method == 'POST':
        # If the form is being submitted, populate the form with the submitted data AND the existing task instance
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save() # Save the changes to the existing task
            return redirect('tasks:matrix') # Redirect back to the main matrix view
    else:
        # If it's a GET request (just loading the page), populate the form with the existing task's data
        form = TaskForm(instance=task)

    # Render the same form template, but with the pre-populated form
    return render(request, 'tasks/task_form.html', {'form': form})
