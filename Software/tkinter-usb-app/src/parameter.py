import time
from tkinter import Button, E, Entry, Frame, Label, LabelFrame, StringVar, W


class ParameterApp:
    def __init__(self, master, write_command, return_to_main):
        self.master = master
        self.write_command = write_command
        self.return_to_main = return_to_main

        # Initialize the parameter dictionary
        self.parameter = {}

        # Create a frame for the ParameterApp
        self.frame_parameter = Frame(master)
        self.frame_parameter.grid(column=1, row=0, padx=1, pady=1, sticky=W)

        # Create a LabelFrame for editing parameters
        self.frame_edit = LabelFrame(master, text="Parameters")
        self.frame_edit.grid(column=0, row=1, padx=1, pady=1, sticky=W)

        # Add labels and entry fields for parameters
        self.parameter_labels_entries = []
        self.parameter_vars = {}
        parameter_keys = [
            "kP",
            "kI",
            "kD",
            "targetNa",
            "toleranceNa",
            "startX",
            "startY",
            "measureMs",
            "direction",
            "maxX",
            "maxY",
            "multiplicator",
        ]
        for i, key in enumerate(parameter_keys):
            parameter_label = Label(self.frame_edit, text=f"{key}:")
            parameter_var = StringVar()
            parameter_entry = Entry(self.frame_edit, textvariable=parameter_var)
            self.parameter_labels_entries.append((parameter_label, parameter_entry))
            self.parameter_vars[key] = parameter_var

        # Grid the labels and entry fields for parameters
        for i, (label, entry) in enumerate(self.parameter_labels_entries):
            label.grid(column=0, row=i, padx=1, pady=1, sticky=W)
            entry.grid(column=1, row=i, padx=1, pady=1)

        # Add Stop button to return to the main interface
        self.btn_back = Button(
            self.frame_parameter, text="Stop", command=self.return_to_main
        )
        self.btn_back.grid(column=0, row=0, padx=1, pady=1, sticky=W)

        # Add Apply and Default buttons
        self.btn_apply_parameter_setting = Button(
            self.frame_parameter, text="Apply", command=self.apply_parameters
        )
        self.btn_apply_parameter_setting.grid(column=1, row=0, padx=1, pady=1, sticky=W)

        self.btn_set_parameter_default = Button(
            self.frame_parameter, text="Default", command=self.set_default_parameters
        )
        self.btn_set_parameter_default.grid(column=2, row=0, padx=1, pady=1, sticky=E)

    def request_parameter(self):
        self.write_command("PARAMETER,?")

    def apply_parameters(self):
        parameters = [entry.get() for _, entry in self.parameter_labels_entries]
        sendstring = f"PARAMETER,{','.join(parameters)}"
        try:
            self.write_command(sendstring)
            time.sleep(0.1)
            self.request_parameter()
        except Exception as e:
            error_message = f"ERROR in apply_parameters {e}"
            print(error_message)

    def set_default_parameters(self):
        try:
            self.write_command("PARAMETER,DEFAULT")
            time.sleep(0.1)
            self.request_parameter()

        except Exception as e:
            error_message = f"ERROR in set_default_parameters {e}"
            print(error_message)

    def update_data(self, message):
        """Updates the Parameter interface with new data"""
        data = message.split(",")
        if data[0] == "PARAMETER":
            key = data[1]
            value = data[2]
            self.parameter[key] = value
            self.parameter_vars[key].set(value)
