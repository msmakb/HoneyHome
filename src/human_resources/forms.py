from django import forms
from django.forms import ModelForm
from main.models import Person
from .models import Employee, Task


class DateInput(forms.DateInput):
    # Adjusting the date input
    input_type = 'date'


class DateTimeInput(forms.DateInput):
    # Adjusting the date time input
    input_type = 'datetime-local'


class AddPersonForm(ModelForm):

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
        }

    def clean_phone_number(self) -> str:
        """
        This function to validate the phone number inserted with the following format:
        The pattern format is not secure enough to be the only validator.
        Format: [+][1 to 3 numbers][space][9 to 14 numbers].

        Raises:
            forms.ValidationError: The phone number must be started with '+'.
            forms.ValidationError: Only '+' sing in the begging and digits are acceptable.
            forms.ValidationError: There must be a space ' ' between the country key and the phone number.
            forms.ValidationError: The country key must be between 1-3 digits.
            forms.ValidationError: The phone number must be between 9-14 digits.

        Returns:
            str: A valid format for phon number
        """
        phone_number = self.cleaned_data.get('phone_number')
        splitted = phone_number.split(' ')
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


class EmployeePositionForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(EmployeePositionForm, self).__init__(*args, **kwargs)

        # Get a copy list of employees positions
        POSITIONS = Employee.POSITIONS.copy()

        # Get all employees
        employees = Employee.objects.all()
        for employee in employees:
            existingPosition = employee.position
            # This is on updating employee's record
            if 'instance' in kwargs:
                # Ignore if the existing position is the instance position
                if kwargs['instance'].position == existingPosition:
                    continue
            # If the position is exists, remove it from available positions
            if (f'{existingPosition}', f'{existingPosition}') in POSITIONS:
                POSITIONS.remove(
                    (f'{existingPosition}', f'{existingPosition}'))

        widget = forms.Select(
            attrs={
                'required': True,
                'class': 'form-control',
            }
        )

        self.fields['position'] = forms.ChoiceField(
            choices=POSITIONS,
            widget=widget
        )

    class Meta:
        model = Employee
        fields = ['position', ]


class AddTaskForm(ModelForm):

    def __init__(self, requester_position, *args, **kwargs):
        super(AddTaskForm, self).__init__(*args, **kwargs)

        # Get the current field's choices
        CHOICES = list(self.fields['employee'].choices)

        choices_to_remove = []
        # Loop to get the choices to remove
        for choice in CHOICES:
            # Avoid the first choice '......' from django
            if not choice[0]:
                continue
            else:
                # Get the employee position by there name
                employee_position = Employee.objects.get(
                    person__name=choice[1]).position
            # If it's CEO add the choice to be removed
            if employee_position == "CEO":
                choices_to_remove.append(choice)
            # If it's HR and the requester also the HR, add the choice to be removed
            if employee_position == "Human Resources":
                if requester_position == "Human Resources":
                    choices_to_remove.append(choice)

        # Remove the choices in 'choices_to_remove' list
        for choice in choices_to_remove:
            CHOICES.remove(choice)

        # Update the choices list
        self.fields['employee'].choices = CHOICES
        self.fields['employee'].widget.choices = CHOICES

    class Meta:
        model = Task
        fields = [
            'employee',
            'name',
            'description',
            'deadline_date',
        ]
        widgets = {
            'employee': forms.Select(
                attrs={'required': True, 'class': 'form-control'}
            ),

            'name': forms.TextInput(
                attrs={
                    'required': True,
                    'class': 'form-control',
                    'placeholder': 'Task',
                }
            ),

            'description': forms.Textarea(
                attrs={
                    'required': False,
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
        }
