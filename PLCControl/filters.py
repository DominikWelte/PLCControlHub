import django_filters
import django
from django import forms
from django_filters import ModelMultipleChoiceFilter, MultipleChoiceFilter, ModelChoiceFilter
from .models import Project, Variables, Connectionparameters


class ProjectFilter(django_filters.FilterSet):
    projectnumber = ModelChoiceFilter(
        field_name="projectnumber",
        label="PLC_Name and projectnumber",
        queryset=Project.objects.all(),
        widget=django.forms.Select,
    )

    class Meta:
        model = Project
        fields = ["projectnumber"]


class VariableFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='variable', lookup_expr='icontains')
