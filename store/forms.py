from django import forms
from .models import Category


class ProductFilterForm(forms.Form):
    product_name = forms.CharField(label='Search', max_length=100, required=False)
    category_name = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label='All Categories',
                                           required=False)


class ProductAddForm(forms.Form):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label='All Categories',
                                           help_text="Select category")
    product_name = forms.CharField(max_length=50, help_text="Enter product name")
    characteristics = forms.CharField(widget=forms.Textarea, max_length=100, help_text="Enter product characteristics")
