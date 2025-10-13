from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'category', 'due_date', 'urgent', 'important', 'tags']
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-input', 'type': 'datetime-local'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'urgent': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'important': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }