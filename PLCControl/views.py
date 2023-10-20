from django.shortcuts import render
import pyads
import threading
import time

from django.views import View

global_value_buffer = []
stop_thread_logging_worker = False


class PLCConnect(View):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.infotext = None
        self.stop_event = threading.Event()
        self.AMSnetID = "5.64.35.8.1.1"
        # self.AMSnetID = request.GET.get("AMSnetID")
        self.AMSnetID = self.remove_whitespace_from_string(self.AMSnetID)
        self.IP = "10.109.21.38"
        # self.IP = request.GET.get("IP")
        self.IP = self.remove_whitespace_from_string(self.IP)
        self.port = 851
        # self.port = request.GET.get("port")
        self.variable = "Handling.LightSaberR_StartPos_Upperfront.cfgTolerance"
        # self.variable = request.GET.get("variable")
        self.variable = self.remove_whitespace_from_string(self.variable)
        self.value = ""
        self.logging = False
        self.logging_thread = None

    def get(self, request):
        value_buffer = []
        try:
            self.plc = pyads.Connection(self.AMSnetID, self.port, self.IP)
            self.plc.open()
            self.value = self.plc.read_by_name(self.variable)
            self.infotext = "connection to PLC established"
            global stop_thread_logging_worker
            if "logging_start" in request.GET:
                self.logging = True
                stop_thread_logging_worker = False
                self.logging_thread = threading.Thread(target=self.logging_worker)
                self.logging_thread.start()
            if "logging_stop" in request.GET:
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
                   "value_buffer": value_buffer}
        return render(request, 'plcconnect.html', context=context)

    def logging_worker(self):
        first_cycle = True
        while True:
            value_old = self.value
            symbol = self.plc.get_symbol(self.variable)
            time_in_ms = time.time()
            self.value = self.plc.read_by_name(self.variable)
            global stop_thread_logging_worker
            if first_cycle:
                global_value_buffer.append((time_in_ms, symbol.name, self.value))
                first_cycle = False
            elif self.value != value_old:
                global_value_buffer.append((time_in_ms, symbol.name, self.value))
            if stop_thread_logging_worker:
                break

    @staticmethod
    def remove_whitespace_from_string(string):
        string = string.replace(" ", "")
        return string

