# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator, MaxLengthValidator
from django.db.models import ForeignKey


class Project(models.Model):
    PLC_Name = models.CharField(max_length=100)
    projectnumber = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(99999)]
    )

    def __str__(self):
        return f"{self.PLC_Name} {self.projectnumber}"


class Connectionparameters(models.Model):
    amsnet_id = models.CharField(max_length=100)
    ip_adresse = models.CharField(max_length=100)
    port = models.PositiveIntegerField(
        validators=[MinLengthValidator(3), MaxLengthValidator(3)])
    project = ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return f"AMSnetID = {self.amsnet_id}"


class Variables(models.Model):
    variable = models.CharField(max_length=255)
    variables = ForeignKey(Connectionparameters, on_delete=models.CASCADE)

    def __str__(self):
        return self.variable

