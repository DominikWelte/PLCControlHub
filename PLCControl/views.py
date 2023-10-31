from django.shortcuts import render, redirect
import pyads
import threading
import time
from django.views import View
from .forms import GetPLCConnectionValuesForm, GetPLCVariablesFrom
from .models import Project, Connectionparameters, Variables
from .filters import ProjectFilter, VariableFilter

global_value_buffer = []
stop_thread_logging_worker = False


def remove_whitespace_from_string(string):
    string = string.replace(" ", "")
    return string


def home_view(request):
    connect = True
    back = False
    if request.method == 'POST':
        if "add" in request.POST:
            back = True
        form = GetPLCConnectionValuesForm(request.POST)
        if form.is_valid():
            PLC_Name = remove_whitespace_from_string(form.cleaned_data['PLC_Name'])
            projectnumber = form.cleaned_data['Projectnumber']
            amsnet_id = remove_whitespace_from_string(form.cleaned_data['AMSnetID'])
            ip_adresse = remove_whitespace_from_string(form.cleaned_data['IP'])
            port = form.cleaned_data['port']
            project, created_project = Project.objects.get_or_create(PLC_Name=PLC_Name, projectnumber=projectnumber)
            if created_project:
                connection = Connectionparameters.objects.create(amsnet_id=amsnet_id, ip_adresse=ip_adresse, port=port, project=project)
            return redirect("home")
    elif request.method == "GET":
        data = Project.objects.all()
        myFilter = ProjectFilter(request.GET, queryset=data)
        context = {
            "myFilter": myFilter,
            "connect": connect,
        }
        id = request.GET.get("projectnumber")
        if "connect" in request.GET and id:
            connect_dict = get_connection_parameters_for_plc(id=id)
            context = {"connect_dict": connect_dict,
                       "id": id}
            return render(request, "plcconnect.html", context=context)
        return render(request, "home.html", context)
    else:
        form = GetPLCConnectionValuesForm()
    connect = False
    context = {'form': form,
               'connect': connect,
               'back': back}
    return render(request, 'home.html', context=context)


def get_connection_parameters_for_plc(id):
    obj = Connectionparameters.objects.select_related('project').get(id=id)
    connect_dict = {
        "amsnet_id": obj.amsnet_id,
        "ip_adresse": obj.ip_adresse,
        "port": obj.port,
    }
    return connect_dict


class Connect(View):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def get(request, id):
        connect_dict = get_connection_parameters_for_plc(id)
        amsnet_id = connect_dict["amsnet_id"]
        ip_adresse = connect_dict["ip_adresse"]
        port = connect_dict["port"]
        try:
            plc = pyads.Connection(amsnet_id, port, ip_adresse)
            plc.open()
            infotext = "connection to PLC established"
        except pyads.ADSError as e:
            infotext = f"{e}"
        except ValueError as e:
            infotext = f"connection to PLC failed with error {e}"
        except TypeError as e:
            infotext = f"connection to PLC failed with error {e}"
        context = {
            "infotext": infotext,
            "id": id,
        }
        return render(request, "plcconnected.html", context=context)


class AddVariable(View):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get(self, request, id):
        variables_for_project = Variables.objects.filter(variables=id)
        form = GetPLCVariablesFrom()
        if not variables_for_project:
            context = {"id": id,
                       "filter": False,
                       "form": form}
        else:
            myFilter = VariableFilter(request.GET, queryset=Variables.objects.all())
            if "search" in request.GET:
                variables_for_project = myFilter.qs
            context = {"id": id,
                       "filter": True,
                       "variables_for_project": variables_for_project,
                       "myFilter": myFilter,
                       "form": form}
        return render(request, "add_variable.html", context=context)

    def post(self, request, id):
        form = GetPLCVariablesFrom(request.POST)
        if form.is_valid():
            variable = remove_whitespace_from_string(form.cleaned_data["variable"])
            connectionparameters_instance = Connectionparameters.objects.get(id=id)
            Variables.objects.create(
                variable=variable,
                variables=connectionparameters_instance
            )
        return render(request, "add_variable.html")

