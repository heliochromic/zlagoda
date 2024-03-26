from django import forms
from .models import Category


class ProductFilterForm(forms.Form):
    product_name = forms.CharField(label='Search', max_length=100, required=False)
    category_name = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label='All Categories', required=False)
