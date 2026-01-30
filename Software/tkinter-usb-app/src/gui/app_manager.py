from tkinter import Frame

import measure
from adjust import AdjustApp
from parameter import ParameterApp
from sinus import SinusApp
from tunnel import TunnelApp


class AppManager:
    def __init__(
        self,
        master,
        write_command=None,
        return_to_main=None,
        disable_menu_cb=None,
        enable_menu_cb=None,
    ):
        self.master = master
        self.write_command = write_command
        self.return_to_main_cb = return_to_main
        self.disable_menu_cb = disable_menu_cb
        self.enable_menu_cb = enable_menu_cb

        # Frame that holds app content (placed on the right)
        self.app_frame = Frame(self.master)
        self.app_frame.pack(side="right", fill="both", expand=True)

        # App instances
        self.measure_app = None
        self.tunnel_app = None
        self.adjust_app = None
        self.sinus_app = None
        self.parameter_app = None

        self.target_adc = 0
        self.tolerance_adc = 0

    def set_write_command(self, write_command):
        self.write_command = write_command

    def _clear_app_frame(self):
        for widget in self.app_frame.winfo_children():
            widget.destroy()

    def disable_menu(self):
        if callable(self.disable_menu_cb):
            self.disable_menu_cb()

    def enable_menu(self):
        if callable(self.enable_menu_cb):
            self.enable_menu_cb()

    def open_measure(self, simulate=False):
        self._clear_app_frame()
        self.measure_app = measure.MeasureApp(
            master=self.app_frame,
            write_command=self.write_command,
            return_to_main=self.return_to_main_cb,
            simulate=simulate,
        )
        self.disable_menu()

    def open_measure_simulate(self):
        self.open_measure(simulate=True)

    def open_tunnel(self, simulate=False):
        self._clear_app_frame()
        self.tunnel_app = TunnelApp(
            master=self.app_frame,
            write_command=self.write_command,
            return_to_main=self.return_to_main_cb,
            target_adc=self.target_adc,
            tolerance_adc=self.tolerance_adc,
            simulate=simulate,
        )
        self.disable_menu()

    def open_tunnel_simulate(self):
        self.open_tunnel(simulate=True)

    def open_adjust(self):
        self._clear_app_frame()
        self.adjust_app = AdjustApp(
            master=self.app_frame,
            write_command=self.write_command,
            return_to_main=self.return_to_main_cb,
        )
        self.disable_menu()

    def open_sinus(self):
        self._clear_app_frame()
        self.sinus_app = SinusApp(
            master=self.app_frame,
            write_command=self.write_command,
            return_to_main=self.return_to_main_cb,
        )
        if self.sinus_app:
            try:
                self.sinus_app.request_sinus()
            except Exception:
                pass
        self.disable_menu()

    def open_parameter(self):
        self._clear_app_frame()
        self.parameter_app = ParameterApp(
            self.app_frame, self.write_command, self.return_to_main_cb
        )
        try:
            self.parameter_app.request_parameter()
        except Exception:
            pass
        self.disable_menu()

       # Helpers used by MasterGui.dispatch_received_data:
    def get_adjust_app(self):
        return self.adjust_app

    def get_parameter_app(self):
        return self.parameter_app

    def get_tunnel_app(self):
        return self.tunnel_app

    def get_measure_app(self):
        return self.measure_app

    def get_sinus_app(self):
        return self.sinus_app
