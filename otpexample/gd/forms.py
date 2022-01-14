from django import forms
from .models import ,community_comment

class community_comment_form(forms.ModelForm):
    class Meta:
        model = community_comment
        fields = ( 'post_comment',)
        widgets={
            'post_comment':forms.Textarea(attrs={'class':'form-control'})
        }