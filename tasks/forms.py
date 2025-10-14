from django import forms
from .models import Task, Comment, Attachment

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'category', 'due_date', 'urgent', 'important', 'tags', 'status']
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-input', 'type': 'datetime-local'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'urgent': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'important': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'status': forms.Select(attrs={'class': 'form-select'})
        }

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