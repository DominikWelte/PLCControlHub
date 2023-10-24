import django_filters
import django
from django import forms
from django_filters import MultipleChoiceFilter, ModelMultipleChoiceFilter
from .models import Project
from django_filters.widgets import LinkWidget


class ProjectFilter(django_filters.FilterSet):
    projectnumber = django_filters.ModelChoiceFilter(
        field_name='projectnumber',
        label="Projectname and projectnumber",
        queryset=Project.objects.all(),
        widget=django.forms.Select,
    )

    class Meta:
        model = Project
        fields = ['projectnumber']
