from django import forms

class GetPLCConnectionValuesForm(forms.Form):
    PLC_Name = forms.CharField(label='PLC_Name', max_length=100, required=True)
    Projectnumber = forms.IntegerField(label='Projectnumber', required=True)
    AMSnetID = forms.CharField(label='Insert AMSnetID', max_length=100, required=True)
    IP = forms.CharField(label='Insert IP of the PLC', required=True)
    port = forms.IntegerField(label='Insert Port of the PLC', required=True)
    variable = forms.CharField(label='Insert variable to be read', required=True)

