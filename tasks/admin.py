from django.contrib import admin

from django.contrib import admin
from .models import Task, Tag, Comment, Attachment

# To make the admin interface more useful, we can customize how models are displayed.

class CommentInline(admin.TabularInline):
    """Allows comments to be viewed and added directly from the Task change page."""
    model = Comment
    extra = 1  # Show one extra blank comment form by default
    readonly_fields = ('author', 'created_at')

class AttachmentInline(admin.TabularInline):
    """Allows attachments to be viewed and added directly from the Task change page."""
    model = Attachment
    extra = 1 # Show one extra blank attachment form by default
    readonly_fields = ('uploaded_by', 'uploaded_at')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Customizes the admin interface for the Task model."""
    list_display = ('title', 'status', 'category', 'assignee', 'due_date', 'urgent', 'important')
    list_filter = ('status', 'category', 'urgent', 'important', 'assignee')
    search_fields = ('title', 'description', 'ticket_id')
    inlines = [CommentInline, AttachmentInline]
    readonly_fields = ('created_at', 'ticket_id')
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'ticket_id')
        }),
        ('Classification', {
            'fields': ('urgent', 'important', 'category', 'tags')
        }),
        ('Assignment & Status', {
            'fields': ('status', 'requester', 'assignee', 'due_date')
        }),
        ('Metadata', {
            'fields': ('created_at', 'is_archived')
        }),
    )

    def save_model(self, request, obj, form, change):
        """Automatically set the reporter to the current user when a task is created."""
        if not obj.pk:  # If the object is being created
            obj.requester = request.user
        super().save_model(request, obj, form, change)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Customizes the admin interface for the Tag model."""
    search_fields = ('name',)

# Note: Comment and Attachment are managed through the Task admin via inlines,
# so they don't need their own detailed admin registration unless desired for standalone access.
# If you wanted to see them as separate items in the admin, you would add:
# admin.site.register(Comment)
# admin.site.register(Attachment)
