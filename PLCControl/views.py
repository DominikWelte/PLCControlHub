from django.shortcuts import render, redirect
import pyads
import threading
import time
from django.views import View
from .forms import ConnectPLCform
from .models import Project, Connectionparameters, Variables

global_value_buffer = []
stop_thread_logging_worker = False


class PLCConnect(View):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.plc = None
        self.infotext = None
        self.AMSnetID = ""
        self.IP = ""
        self.port = 0
        self.variable = ""
        self.value = ""
        self.logging = False
        self.logging_thread = None
        self.status = ""
        self.init_done = True

    def get(self, request):
        value_buffer = []
        plc_dict = {}
        try:
            if "connect" in request.GET:
                plc_dict = self.get_plc_dict(request)
                self.plc = pyads.Connection(self.AMSnetID, self.port, self.IP)
                self.plc.open()
                self.value = self.plc.read_by_name(self.variable)
                self.infotext = "connection to PLC established"
                self.status = "Connected to Beckhoff PLC"
            if "update" in request.GET:
                self.value = self.plc.read_by_name(self.variable)
            global stop_thread_logging_worker
            if "logging_start" in request.GET:
                plc_dict = plc_dict
                self.logging = True
                stop_thread_logging_worker = False
                self.logging_thread = threading.Thread(target=self.logging_worker)
                self.logging_thread.start()
            if "logging_stop" in request.GET:
                plc_dict = plc_dict
                global global_value_buffer
                value_buffer = global_value_buffer.copy()
                global_value_buffer = []
                self.logging = False
                stop_thread_logging_worker = True
        except pyads.ADSError as e:
            if e.err_code == 1808:
                self.infotext = f"Connection to PLC failed with error {e}. <br>" \
                           f" &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp Please check the spelling of your variable {self.variable}. <br>"
        except ValueError as e:
            self.infotext = f"connection to PLC failed with error {e}"
        except TypeError as e:
            self.infotext = f"connection to PLC failed with error {e}"
        if not self.value:
            self.value = "failed to read from PLC"

        context = {"infotext": self.infotext,
                   "value": self.value,
                   "variable": self.variable,
                   "logging": self.logging,
                   "value_buffer": value_buffer,
                   "status": self.status,
                   "plc_dict": plc_dict}
        return render(request, 'plcconnect.html', context=context)

    def logging_worker(self):
        #with open(r"\log\log.txt", "a") as file:
            first_cycle = True
            while True:
                value_old = self.value
                symbol = self.plc.get_symbol(self.variable)
                time_in_ms = time.time()
                self.value = self.plc.read_by_name(self.variable)
                global stop_thread_logging_worker
                if first_cycle:
                    n = 0
                    global_value_buffer.append((time_in_ms, symbol.name, self.value))
                    first_cycle = False
                    #file.write(f"{global_value_buffer[n]}")
                    n += 1
                elif self.value != value_old:
                    global_value_buffer.append((time_in_ms, symbol.name, self.value))
                    #file.write(f"{global_value_buffer[n]}")
                    n += 1
                if stop_thread_logging_worker:
                    break

    def get_plc_dict(self, request):
        self.AMSnetID = request.GET.get("AMSnetID")
        self.AMSnetID = self.remove_whitespace_from_string(self.AMSnetID)
        self.IP = request.GET.get("IP")
        self.IP = self.remove_whitespace_from_string(self.IP)
        self.port = int(request.GET.get("port"))
        self.variable = request.GET.get("variable")
        self.variable = self.remove_whitespace_from_string(self.variable)
        plc_dict = {"AMSnetID": self.AMSnetID,
                    "IP": self.IP,
                    "port": self.port,
                    "variable": self.variable}
        return plc_dict

def remove_whitespace_from_string(string):
    string = string.replace(" ", "")
    return string


def home_view(request):
    if request.method == 'POST':
        form = ConnectPLCform(request.POST)
        if form.is_valid():
            projectname = remove_whitespace_from_string(form.cleaned_data['Projektname'])
            projectnumber = form.cleaned_data['Projectnumber']
            amsnet_id = remove_whitespace_from_string(form.cleaned_data['AMSnetID'])
            ip_adresse = remove_whitespace_from_string(form.cleaned_data['IP'])
            port = form.cleaned_data['port']
            variable = remove_whitespace_from_string(form.cleaned_data['variable'])
            connection, created = Connectionparameters.objects.get_or_create(amsnet_id=amsnet_id, ip_adresse=ip_adresse, port=port)
            variable_obj, created = Variables.objects.get_or_create(variable=variable)
            project = Project.objects.create(
                name=projectname,
                projectnumber=projectnumber,
                amsnet_id=connection,
            )
            project.amsnet_id.variables.add(variable_obj.id)
            return redirect("plcconnect")
    else:
        form = ConnectPLCform()

    return render(request, 'home.html', {'form': form})

