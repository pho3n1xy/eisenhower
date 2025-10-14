from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Task
from django.http import HttpResponseRedirect
from django.db.models import Q
from .forms import TaskForm, CommentForm, AttachmentForm, StatusUpdateForm


#Decorator to protect the matrix view
@login_required
def matrix_view(request):
    """
    This view handles the logic for displaying the main Eisenhower Matrix.
    It fetches all non-archived tasks and categorizes them into the four quadrants.
    """

    # This is the updated query
    tasks = Task.objects.filter(
        assignee=request.user, 
        is_archived=False
    ).exclude(
        Q(status=Task.Status.RESOLVED) | Q(status=Task.Status.CLOSED)
    )
    
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
    
    context = {
        'form': form,
        'mode': 'create'
    }

    # This line MUST be at the base indentation level of the function.
    # It should NOT be inside the 'else' block.
    return render(request, 'tasks/task_form.html', context)


        
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
    
    context = {
        'form': form,
        'mode': 'edit'
    }

    # Render the same form template, but with the pre-populated form
    return render(request, 'tasks/task_form.html', context)

@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk, assignee=request.user)

    if request.method=="POST":
        task.delete()
        return redirect('tasks:matrix')
    
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})


@require_POST # ensure view can only be accessed via POST
@login_required
def toggle_complete():
    task = get_object_or_404(Task, pk=pk, assignee=request.user)
    task.is_completed = not task.is_completed
    task.save()
    return redirect('tasks:matrix')

@require_POST
@login_required
def archive_completed_tasks(request):
    tasks_to_archive = Task.objects.filter(assignee=request.user, is_completed=True, is_archived=False)
    tasks_to_archive.update(is_archive=True)
    return redirect('tasks:matrix')


@login_required
def task_detail_view(request, pk):
    task = get_object_or_404(Task, pk=pk, assignee=request.user)
    comments = task.comments.all().order_by('-created_at')
    attachments = task.attachments.all().order_by('-uploaded_at')

    if request.method == 'POST':
        # Check if the comment form was submitted
        form_identifier = request.POST.get('form_identifier')

        if form_identifier == 'add_comment':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.task = task
                comment.author = request.user
                comment.save()
                return redirect('tasks:task_detail', pk=task.pk)

        # Check if the attachment form was submitted
        elif form_identifier == 'add_attachment':
            attachment_form = AttachmentForm(request.POST, request.FILES)
            if attachment_form.is_valid():
                attachment = attachment_form.save(commit=False)
                attachment.original_filename = attachment_form.cleaned_data['file'].name
                attachment.task = task
                attachment.uploaded_by = request.user
                attachment.save()
                return redirect('tasks:task_detail', pk=task.pk)
            
        # --- this block handles the status update ---
        elif form_identifier == 'update_status':
            status_form = StatusUpdateForm(request.POST, instance=task)
            if status_form.is_valid():
                status_form.save()

                return redirect('tasks:task_detail', pk=task.pk)

    # For a GET request, create empty forms
    comment_form = CommentForm()
    attachment_form = AttachmentForm()
    status_form = StatusUpdateForm(instance=task)

    context = {
        'task': task,
        'comments': comments,
        'attachments': attachments,
        'comment_form': comment_form,
        'attachment_form': attachment_form,
        'status_form': status_form
    }
    return render(request, 'tasks/task_detail.html', context)