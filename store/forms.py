from django import forms
from .models import Category


class ProductFilterForm(forms.Form):
    search = forms.CharField(label='Search', max_length=100, required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label='All Categories', required=False)
