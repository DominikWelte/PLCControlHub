from django.contrib import admin
from .models import Project, Connectionparameters, Variables
# Register your models here.
admin.site.register(Project)
admin.site.register(Connectionparameters)
admin.site.register(Variables)
