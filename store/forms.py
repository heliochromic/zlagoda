import re

from django import forms

from .models import Category, Employee


class ProductFilterForm(forms.Form):
    product_name = forms.CharField(label='Search', max_length=100, required=False)
    category_name = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label='All Categories',
                                           required=False)


class ProductAddForm(forms.Form):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label='All Categories',
                                      help_text="Select category")
    product_name = forms.CharField(max_length=50, help_text="Enter product name")
    characteristics = forms.CharField(widget=forms.Textarea, max_length=100, help_text="Enter product characteristics")


class EmployeeFilterForm(forms.Form):
    employee_name = forms.CharField(label='Search', max_length=100, required=False)
    empl_role_choices = Employee.objects.values_list('empl_role', flat=True).distinct()
    empl_role_choices = [(role, role) for role in empl_role_choices]
    empl_role_choices.insert(0, ('', 'All Roles'))

    employee_role = forms.ChoiceField(choices=empl_role_choices, required=False)


class EmployeeAddForm(forms.Form):
    employee_id = forms.CharField(max_length=10, help_text="Enter employee id")
    employee_name = forms.CharField(max_length=50, help_text="Enter employee name")
    employee_surname = forms.CharField(max_length=50, help_text="Enter employee surname")
    employee_patronymic = forms.CharField(max_length=50, required=False,
                                                 help_text="Enter patronymic")
    employee_role = forms.CharField(max_length=10, help_text="Enter employee role")
    salary = forms.DecimalField(max_digits=14, decimal_places=4, help_text="Enter employee salary")
    date_of_birth = forms.DateField(help_text="Enter employee date of birth")
    date_of_start = forms.DateField(help_text="Enter date of employee work started")
    phone_number = forms.CharField(max_length=13, help_text="Enter employee phone_number")

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        phone_number_pattern = r'^\+?1?\d{9,15}$'
        if not re.match(phone_number_pattern, phone_number):
            raise forms.ValidationError("Please enter a valid phone number.")
        return phone_number

    city = forms.CharField(max_length=50, help_text="Enter employee city")
    street = forms.CharField(max_length=50, help_text="Enter employee street")
    zip_code = forms.CharField(max_length=9, help_text="Enter employee zip code")