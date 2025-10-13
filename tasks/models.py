import uuid
from django.db import models
from django.contrib.auth.models import User

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
    description = models.TextField(blank=True, null=True, help_text="Detailed notes for the task")
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(blank=True, null=True, help_text="When the task is scheduled to be done")

    # --- Eisenhower Matrix Fields ---
    urgent=models.BooleanField(default=False)
    important= models.BooleanField(default=False)

    # --- Ticketing System Fields ---

    #creates unique identifier for every ticket.. 
    ticket_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    status = models.CharField(max_length=22, choices=Status.choices, default=Status.OPEN)
    category = models.CharField(max_length=22, choices=Category.choices, default=Category.GENERAL)
    requester = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='requested_tasks')
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    tags = models.ManyToManyField(Tag, blank=True)

    # For "Q4 Delete" workflow -> "non-destructive delete"
    is_archived = models.BooleanField(default=False, help_text="Marks a task as archived instead of deleting it.")

    def __str__(self):
        return f"{self.title} ({self.ticket_id})"

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
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'Attachment for {self.task.title}'

