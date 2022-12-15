from django import forms
from django.db.models.query import QuerySet
from django.forms import ModelForm
from django.http import HttpRequest

from main import constants
from main.models import Person
from main.utils import getUserRole, clean_form_created_by, clean_form_updated_by

from .models import Employee, Task


class DateInput(forms.DateInput):
    # Adjusting the date input
    input_type = 'date'


class DateTimeInput(forms.DateInput):
    # Adjusting the date time input
    input_type = 'datetime-local'


class AddPersonForm(ModelForm):

    def __init__(self, request: HttpRequest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not isinstance(request, HttpRequest):
            raise TypeError("Invalid request object!")
        self.request: HttpRequest = request

    class Meta:
        model = Person
        fields = [
            'name',
            'gender',
            'nationality',
            'date_of_birth',
            'address',
            'contacting_email',
            'phone_number',
            'created_by',
            'updated_by',
        ]
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'required': True,
                    'class': 'form-control',
                    'placeholder': 'Full Name',
                }
            ),

            'gender': forms.Select(
                attrs={
                    'required': True,
                    'class': 'form-control',
                }
            ),

            'nationality': forms.Select(
                attrs={
                    'required': True,
                    'class': 'form-control',
                }
            ),

            'date_of_birth': DateInput(
                attrs={
                    'required': False,
                    'class': 'form-control',
                    'data-provide': 'datepicker',
                }
            ),

            'address': forms.TextInput(
                attrs={
                    'required': False,
                    'class': 'form-control',
                    'placeholder': 'Address',
                }
            ),

            'contacting_email': forms.EmailInput(
                attrs={
                    'required': True,
                    'class': 'form-control',
                    'placeholder': 'Contacting Email',
                }
            ),
            'phone_number': forms.TextInput(
                attrs={
                    'required': True,
                    'class': 'form-control',
                    'placeholder': '+123 123456789',
                    #  format: '[+][1 to 3 numbers][space][9 to 14 numbers]'
                    'pattern': "[+][0-9]{1,3} [0-9]{9,14}",
                    'type': 'tel',
                }
            ),
            'created_by': forms.HiddenInput(attrs={'required': False}),
            'updated_by': forms.HiddenInput(attrs={'required': False}),
        }

    def clean_created_by(self):
        object_str_representation: str = self.cleaned_data.get('name')
        return clean_form_created_by(self, object_str_representation)

    def clean_updated_by(self):
        return clean_form_updated_by(self)

    def clean_phone_number(self) -> str:
        phone_number: str = self.cleaned_data.get('phone_number')
        splitted: str = phone_number.split(' ')
        # '+' sign in the begging
        if phone_number[0] != '+':
            raise forms.ValidationError(
                "The phone number must be started with '+'.")
        # Check is all digit except the fires index which should be '+'
        try:
            int(splitted[0][1:])
            int(splitted[1])
        except:
            raise forms.ValidationError(
                "Only '+' sing in the begging and digits are acceptable.")
        # Check if there is a space between key and number
        if len(splitted) != 2:
            raise forms.ValidationError(
                "There must be a space ' ' between the country key and the phone number.")
        # Check if the country key is between 1-3 digits
        if len(splitted[0]) > 4 or len(splitted[0]) < 2:
            raise forms.ValidationError(
                "The country key must be between 1-3 digits.")
        # Check if the phone number is between 9-14 digits
        if len(splitted[1]) < 9 or len(splitted[1]) > 14:
            raise forms.ValidationError(
                "The phone number must be between 9-14 digits.")

        return phone_number


class EmployeeForm(ModelForm):

    def __init__(self, request: HttpRequest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not isinstance(request, HttpRequest):
            raise TypeError("Invalid request object!")
        self.request: HttpRequest = request

        # Update the position choices
        POSITIONS: list = list(self.fields['position'].choices)
        employees: QuerySet[Employee] = Employee.getAll()
        for employee in employees:
            existingPosition: str = employee.position
            instance: Employee = kwargs.get('instance')
            if instance:
                if instance.position == existingPosition:
                    continue
            if (f'{existingPosition}', f'{existingPosition}') in POSITIONS:
                POSITIONS.remove(
                    (f'{existingPosition}', f'{existingPosition}'))

        self.fields['position'].choices = POSITIONS
        self.fields['position'].widget.choices = POSITIONS

    class Meta:
        model = Employee
        fields = ['position', 'created_by', 'updated_by']
        widgets = {
            'position': forms.Select(
                attrs={
                    'required': True,
                    'class': 'form-control',
                }
            ),
            'created_by': forms.HiddenInput(attrs={'required': False}),
            'updated_by': forms.HiddenInput(attrs={'required': False}),
        }

    def clean_created_by(self):
        object_str_representation: str = self.cleaned_data.get('position')
        return clean_form_created_by(self, object_str_representation)

    def clean_updated_by(self):
        return clean_form_updated_by(self)


class AddTaskForm(ModelForm):

    def __init__(self, request: HttpRequest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not isinstance(request, HttpRequest):
            raise TypeError("Invalid request object!")
        self.request: HttpRequest = request

        CHOICES = list(self.fields['employee'].choices)
        choices_to_remove: list = []
        for choice in CHOICES:
            if not choice[0]:
                continue
            else:
                employee: Employee = Employee.get(
                    person__name=choice[1])
            if employee.position == constants.ROLES.CEO:
                choices_to_remove.append(choice)
            if employee.position == constants.ROLES.HUMAN_RESOURCES:
                if getUserRole(request) == constants.ROLES.HUMAN_RESOURCES:
                    choices_to_remove.append(choice)

        for choice in choices_to_remove:
            CHOICES.remove(choice)

        self.fields['employee'].choices = CHOICES
        self.fields['employee'].widget.choices = CHOICES

    class Meta:
        model = Task
        fields = [
            'employee',
            'task',
            'description',
            'deadline_date',
            'created_by',
            'updated_by',
        ]
        widgets = {
            'employee': forms.Select(
                attrs={'required': True, 'class': 'form-control'}
            ),

            'task': forms.TextInput(
                attrs={
                    'required': True,
                    'class': 'form-control',
                    'placeholder': 'Task',
                }
            ),

            'description': forms.Textarea(
                attrs={
                    'required': True,
                    'class': 'form-control',
                    'placeholder': 'Description',
                }
            ),

            'deadline_date': DateTimeInput(
                attrs={
                    'required': False,
                    'class': 'form-control',
                    'data-provide': 'datepicker',
                }
            ),
            'created_by': forms.HiddenInput(attrs={'required': False}),
            'updated_by': forms.HiddenInput(attrs={'required': False}),
        }

    def clean_employee(self):
        employee: Employee = self.cleaned_data["employee"]
        employee_choices: list[tuple] = list(self.fields['employee'].choices)
        employee_name: str = employee.person.name
        clean: bool = False
        for choice in employee_choices:
            if employee_name == choice[1]:
                clean = True
                break
        if not clean:
            raise forms.ValidationError(
                "Select a valid choice. That choice is not one of the available choices.")
        return employee

    def clean_created_by(self):
        object_str_representation: str = self.cleaned_data.get('task')
        return clean_form_created_by(self, object_str_representation)

    def clean_updated_by(self):
        return clean_form_updated_by(self)
