from django import forms

class ConnectPLCform(forms.Form):
    Projektname = forms.CharField(label='Projektname', max_length=100, required=True)
    Projectnumber = forms.IntegerField(label='Projektnummer', required=True)
    AMSnetID = forms.CharField(label='Insert AMSnetID', max_length=100, required=True)
    IP = forms.CharField(label='Insert IP of the PLC', required=True)
    port = forms.IntegerField(label='Insert Port of the PLC', required=True)
    variable = forms.CharField(label='Insert variable to be read', required=True)
