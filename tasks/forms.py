from django import forms
from .models import Task, Comment, Attachment
from django.contrib.auth.models import User, Group


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'category', 'urgent', 
            'important', 'tags', 'status', 'requester', 'assignee'
            ]
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'urgent': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'important': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'requester': forms.Select(attrs={'class': 'form-select'}),
            'assignee': forms.Select(attrs={'class': 'form-select'}),
        }

     # This new method adds the filtering logic
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter the 'assignee' dropdown to only show users in the 'Operators' group
        try:
            operators_group = Group.objects.get(name='Operators')
            self.fields['assignee'].queryset = operators_group.user_set.all()
        except Group.DoesNotExist:
            # If the group doesn't exist, the dropdown will be empty
            self.fields['assignee'].queryset = User.objects.none()

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Add a comment...'}),
        }
        labels = {
            'text': '', # This hides the "Text:" label on the form
        }

class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ['file']
        labels = {
            'file': 'Upload a file',
        }

class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # This adds an HTML attribute to the status dropdown widget
        self.fields['status'].widget.attrs.update({
            'class': 'form-select-sm', # A new class for a smaller select box
            'onchange': 'this.form.submit()' # This JavaScript submits the form automatically on change
        })
        self.fields['status'].label = "" # Hide the "Status:" label

class UserTicketForm(forms.ModelForm):
    # add this new field for the file upload
    attachment_file = forms.FileField(
        required=False,
        label = "Attach a file (optional)",
        widget=forms.ClearableFileInput(attrs={'class': 'form-input'})
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 5}),
            'category': forms.Select(attrs={'class': 'form-select'})
        }