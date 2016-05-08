from django.contrib.auth import get_user_model
from django.forms import Form
from django import forms

from common import enums
from .models import UserRole

# Custom user model
User = get_user_model()


class SignUpForm(Form):
    role = forms.TypedChoiceField(
        label="Account Type",
        coerce=int,
        choices=enums.UserRole.choices(),
    )
    first_name = forms.CharField(
        max_length=30,
        label='First Name',
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30,
        label='Last Name',
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )

    def signup(self, request, user):
        UserRole.objects.create(
            user=user, role=self.cleaned_data['role'],
        )
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
