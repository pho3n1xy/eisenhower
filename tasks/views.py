from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Task, Comment, Attachment, Tag, SLAPolicy
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.contrib.auth.models import User, Group
from django.core.exceptions import PermissionDenied
from .forms import TaskForm, CommentForm, AttachmentForm, StatusUpdateForm, UserTicketForm


#helper function to check is user if operator
def is_operator(user):
    #checks if the user is in the "Operators" group
    return user.groups.filter(name='Operators').exists()


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

            if is_operator(user):
                return redirect('tasks:matrix')
            else:
                return redirect('tasks:submit_ticket')
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
    #only allow operators to access this page
    if not is_operator(request.user):
        raise PermissionDenied

    # Get the specific task object we want to edit, or return a 404 error if it doesn't exist
    task = get_object_or_404(Task, pk=pk)

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
    # only allow Operators to access this page
    if not is_operator(request.user): 
        raise PermissionDenied

    task = get_object_or_404(Task, pk=pk)

    if request.method=="POST":
        task.delete()
        return redirect('tasks:matrix')
    
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})


@login_required
def task_detail_view(request, pk):

    #if user is an operator
    if is_operator(request.user):
        task = get_object_or_404(Task, pk=pk)

    else: 
        #regular users can only view tasks they have requested
        task = get_object_or_404(Task, pk=pk, requester=request.user)

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


@login_required
def ticket_list_view(request):
    # Start with all non-archived tasks, ordered by most recently created
    tasks = Task.objects.filter(is_archived=False).order_by('-created_at')

    #Get the filter values from the URL (e.g., ?status=OPEN)
    status_filter = request.GET.get('status')
    requester_filter = request.GET.get('requester')
    assignee_filter = request.GET.get('assignee')

    #Apply filters to the queryset if they exist
    if status_filter: 
        tasks = tasks.filter(status=status_filter)

    if requester_filter:
        tasks = tasks.filter(requester__id=requester_filter)

    if assignee_filter: 
        tasks = tasks.filter(assignee__id=assignee_filter)

    context = {
        'tasks': tasks, 
        'status_choices': Task.Status.choices, #pass choices for the dropdown
        'all_users': User.objects.all(), 
        'current_status': status_filter,
        'current_requester': int(requester_filter) if requester_filter else None,
        'current_assignee': int(assignee_filter) if assignee_filter else None,
    }

    return render(request, 'tasks/ticket_list.html', context)

@login_required
def submit_ticket_view(request):
    if is_operator(request.user):
        # If an operator lands here, send them to the matrix
        return redirect('tasks:matrix')
    
    if request.method == "POST":
        form = UserTicketForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.requester = request.user
            task.assignee = None
            task.status = Task.Status.OPEN
            task.urgent = False
            task.important = False
            task.save()

            uploaded_file = form.cleaned_data.get('attachment_file')
            if uploaded_file:
                Attachment.objects.create(
                    task=task,
                    file=uploaded_file,
                    original_filename=uploaded_file.name,
                    uploaded_by=request.user
                )

            return redirect('tasks:submit_success', ticket_number=task.ticket_number)
        # If the form is invalid, the code falls through to the final return statement below
    else:
        # This handles the initial GET request
        form = UserTicketForm()
    
    # --- THIS LINE IS THE FIX ---
    # It must be at the base indentation level of the function
    # so it can handle all cases that don't redirect (like GET requests).
    return render(request, 'tasks/submit_ticket.html', {'form': form})

@login_required
def submit_success_view(request, ticket_number):
    return render(request, 'tasks/submit_success.html', {'ticket_number': ticket_number})


@login_required
def my_tickets_view(request):
    if is_operator(request.user):
        # Operators should use the full ticket viewer
        return redirect('tasks:ticket_list')

    tasks = Task.objects.filter(requester=request.user, is_archived=False).order_by('-created_at')
    context = {
        'tasks': tasks,
    }
    return render(request, 'tasks/my_tickets.html', context)