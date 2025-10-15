import uuid
import os
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta

def user_directory_path(instance, filename):
    '''
    Generates a unique path for file uploads. 
    Path will be: media/users/<username>/task_<id>/<uuid>-<filename>
    '''

    #get the original filename's extension
    ext = filename.split('.')[-1]
    #create a new, unique filename using UUID
    new_filename=f"{uuid.uuid4()}.{ext}"

    username = instance.uploaded_by.username
    task_id = instance.task.pk
    file_path = os.path.join('users', username, f'task_{task_id}', new_filename)
    return file_path


class Tag(models.Model):
    """Represents a tag or label that can be applied to tasks."""
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
class Task(models.Model):
    """
    Represents a single ticket/task in the Eisenhower Matrix.
    Combines task management with ticketing system features.
    """

    # --- Choices for dropdown fields ---
    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        PENDING = 'PENDING', 'Pending User Response'
        RESOLVED = 'RESOLVED', 'Resolved'
        CLOSED = 'CLOSED', 'Closed'

    class Category(models.TextChoices):
        HARDWARE = 'hardware', 'Hardware'
        SOFTWARE = 'software', 'Software'
        NETWORK = 'network', 'Network'
        ACCESS = 'access', 'Access & Security'
        GENERAL = 'general', 'General Inquiry'
        ACC = 'acc', 'ACC'
        DIALPAD = 'dialpad', 'Dialpad'
        HUBSPOT = 'hubspot', 'Hubspot'
        GOOGLE = 'google', 'Google Workspace'
        APPLE = 'apple', 'Mac Issues'
        WINDOWS = 'windows', 'Windows Issues'
        MICROSOFT = 'microsoft', 'O365 Issues'
        SAP = 'sap', 'SAP Errors'
        
    # --- Core Task Attributes ---
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True, help_text="")
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(blank=True, null=True, help_text="When the task is scheduled to be done")

    # --- Eisenhower Matrix Fields ---
    urgent=models.BooleanField(default=False)
    important= models.BooleanField(default=False)

    # --- Ticketing System Fields ---
    #creates unique identifier for every ticket.. 
    ticket_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    ticket_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    status = models.CharField(max_length=22, choices=Status.choices, default=Status.OPEN)
    category = models.CharField(max_length=22, choices=Category.choices, default=Category.GENERAL)
    requester = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='requested_tasks')
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    tags = models.ManyToManyField(Tag, blank=True)

    # Archiving and Saving Tasks
    is_archived = models.BooleanField(default=False, help_text="Marks a task as archived instead of deleting it.")
    is_completed = models.BooleanField(default=False)

    # --- Fields for the SLA Progress Bar ---
    completed_at = models.DateTimeField(null=True, blank=True)
    paused_at = models.DateTimeField(null=True, blank=True)
    total_paused_duration = models.DurationField(default=timedelta(0))

    # --- save method ---
    def save(self, *args, **kwargs):
        # Check if this is a new task being created
        is_new = self.pk is None

        # If the task is being update, get its old state from the database
        if not is_new:
            old_task = Task.objects.get(pk=self.pk)

            # Check if the task is being paused
            if old_task.status != self.Status.PENDING and self.status == self.Status.PENDING:
                self.paused_at = timezone.now()
            
            # Check is the task is being resumed
            elif old_task.status == self.Status.PENDING and self.status != self.Status.PENDING:
                if self.paused_at:
                    pause_duration = timezone.now() - self.paused_at
                    self.total_paused_duration += pause_duration
                    self.paused_at = None

            # Check if the task is being completed
            if not old_task.is_completed and self.is_completed: 
                self.completed_at = timezone.now()
            
            # Check if it's being Re-opened
            elif old_task.is_completed and not self.is_completed:
                self.completed_at = None

        # Don't set due_date if it's already been provided
        if is_new and not self.due_date:
            try:
                #find the SLA policy that matches this task's quadrant
                policy = SLAPolicy.objects.get(quadrant=self.quadrant)
                self.due_date = timezone.now() + policy.resolution_time
            
            except SLAPolicy.DoesNotExist: 
                pass

        super().save(*args, **kwargs) # Save the object to get a primary key (self.pk)
        
        # If it was a new task, generate the ticket number
        if is_new and not self.ticket_number:
            self.ticket_number = f"OHM{self.pk:13d}"
            # Save again just to update this one field
            super().save(update_fields=['ticket_number'])

    def __str__(self):
        return f"{self.title} ({self.ticket_id})"
    
    @property
    def sla_progress_percent(self):
        if not self.due_date: 
            return 0
        
        sla_duration = self.due_date - self.created_at
        if sla_duration.total_seconds() <= 0:
            return 100
        
        time_elapsed = timezone.now() - self.created_at

        # if it's paused, subtract the time it has been paused so far
        if self.paused_at:
            current_pause_duration = timezone.now() - self.paused_at
            effective_elapsed = time_elapsed - self.total_paused_duration

        else:
            effective_elapsed = time_elapsed - self.total_paused_duration

        # if completed, calculate based on completion time
        if self.completed_at: 
            effective_elapsed = (self.completed_at - self.created_at) - self.total_paused_duration

        progress = (effective_elapsed.total_seconds() / sla_duration.total_seconds()) * 100
        
        return min(progress, 100) # Cap at 100%
    
    @property
    def is_completed(self):
        """Determines if the task is considered complete based on its status."""
        return self.status in [self.Status.RESOLVED, self.Status.CLOSED]

    @property
    def quadrant(self):
        """
        Determines the quadrant for the task based on its urgency and importance.
        """
        if self.important and self.urgent:
            return 'do_first'  # Quadrant 1: Urgent & Important
        elif self.important and not self.urgent:
            return 'schedule'  # Quadrant 2: Important & Not Urgent
        elif not self.important and self.urgent:
            return 'delegate'  # Quadrant 3: Not Important & Urgent
        else:
            return 'delete'  # Quadrant 4: Not Important & Not Urgent
    
    @property
    def get_quadrant_display(self):
        """Returns a human-readable version of the quadrant name."""
        return self.quadrant.replace('_', ' ').title()

class Comment(models.Model):
    """Represents a comment on a task/ticket."""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author} on {self.task.title}'

class Attachment(models.Model):
    """Represents a file attached to a task/ticket."""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to=user_directory_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)

    original_filename = models.CharField(max_length=255)

    def __str__(self):
        return self.original_filename or self.file.name
    

class SLAPolicy(models.Model):
    """Stores the SLA rules, configurable in the admin panel"""
    QUADRANT_CHOICES = [
        ('do_first', 'Do First (Urgent & Important)'),
        ('schedule', 'Schedule (Important & Not Urgent)'),
        ('delegate', 'Queue (Urgent & Not Important)'),
        ('delete', 'Backlog / Archive (Not Urgent & Not Important)'),
    ]

    name = models.CharField(max_length=100, help_text="e.g., Critical, High, Medium, Low")
    quadrant = models.CharField(max_length=10, choices=QUADRANT_CHOICES, unique=True)
    resolution_time = models.DurationField(
        default=timedelta(days=1),
        help_text="Enter a duration, e.g., '3 days', '8 hours', or '1 day 12 hours'."
    )

    def __str__(self):
        return self.name



