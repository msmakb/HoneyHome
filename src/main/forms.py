from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


class CreateUserForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)

        pass_widget = forms.PasswordInput(
                        attrs={
                            'required': True,
                            'class': 'form-control form-control-lg',
                            'placeholder': 'Password',
                        }
                    )

        self.fields['password1'].widget = pass_widget
        self.fields['password2'].widget = pass_widget

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2',
        ]
        widgets = {
                    'username': forms.TextInput(
                        attrs={
                            'required': True,
                            'class': 'form-control form-control-lg',
                            'placeholder': 'UserName',
                        }
                    ),
                    'email': forms.TextInput(
                        attrs={
                            'required': True,
                            'class': 'form-control  form-control-lg',
                            'placeholder': 'Email address',
                        }
                    ),
        }