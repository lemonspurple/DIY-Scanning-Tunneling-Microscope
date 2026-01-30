import os
import sys
import time
import tkinter as tk
from tkinter import VERTICAL, Button, Frame, Label, LabelFrame, Scale, messagebox
from tkinter.ttk import Progressbar

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import config_utils


class AdjustApp:
    def __init__(self, master, write_command, return_to_main):
        self.master = master
        self.write_command = write_command
        self.return_to_main = return_to_main
        self.is_active = True

        # Create a frame to hold the widgets
        self.frame = LabelFrame(master)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Add Stop button to return to the main interface
        self.btn_back = Button(
            self.frame, text="Stop", command=self.wrapper_return_to_main
        )
        self.btn_back.pack(pady=10)

        # Create a LabelFrame for Voltage
        self.voltage_frame = LabelFrame(self.frame, text="ADC Tunnel")
        self.voltage_frame.pack(fill="x", padx=10, pady=10)
        self.voltage_frame.config(height=150)  # Adjust the height of the voltage frame

        # Add a label inside the Voltage frame
        self.voltage_label = Label(self.voltage_frame, text="0", font=("Arial", 20))
        self.voltage_label.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        # Add a label for digits below the voltage_label
        self.digits_label = Label(
            self.voltage_frame, text="Digits: 0", font=("Arial", 10)
        )
        self.digits_label.grid(row=1, column=0, padx=10, pady=10, sticky="n")

        # Add a Progressbar inside the Voltage frame
        self.voltage_progressbar = Progressbar(
            self.voltage_frame,
            style="Thin.Horizontal.TProgressbar",
            orient=VERTICAL,
            length=150,
            mode="determinate",
            maximum=0x7FFF,
        )
        self.voltage_progressbar.grid(
            row=0, column=1, rowspan=2, padx=10, pady=10, sticky="ns"
        )

        # Configure grid columns to center the labels and progress bar
        self.voltage_frame.grid_columnconfigure(0, weight=1)
        self.voltage_frame.grid_columnconfigure(1, weight=0)

        # Create a LabelFrame for Tip
        self.tip_frame = LabelFrame(self.frame, text="")
        self.tip_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.tip_frame.config(height=400)  # Adjust the height of the tip frame

        # Create LabelFrames for Tip X, Tip Y, Tip Z and place them from left to right
        self.tip_x_frame = LabelFrame(self.tip_frame, text="DAC X")
        self.tip_x_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        self.tip_y_frame = LabelFrame(self.tip_frame, text="DAC Y")
        self.tip_y_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        self.tip_z_frame = LabelFrame(self.tip_frame, text="DAC Z")
        self.tip_z_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        # SLIDERS X Y Z
        slider_length = 300
        up = int("FFFF", 16)
        resolution = 100

        # TIP X #########################
        self.slider_x = Scale(
            self.tip_x_frame,
            from_=0,
            to=up,
            orient=VERTICAL,
            length=slider_length,
            showvalue=True,
            resolution=resolution,
        )
        self.slider_x.pack(pady=5)

        # Bind the ButtonRelease-1 event to the on_slider_xyz_button_release function
        self.slider_x.bind("<ButtonRelease-1>", self.on_slider_xyz_button_release)

        self.lb_x = Label(
            self.tip_x_frame, text=self.slider_x.get(), width=10, font=("Arial", 15)
        )
        self.lb_x.pack(pady=5)

        # TIP Y #########################
        self.slider_y = Scale(
            self.tip_y_frame,
            from_=0,
            to=up,
            orient=VERTICAL,
            length=slider_length,
            showvalue=True,
            resolution=resolution,
        )
        self.slider_y.pack(pady=5)

        # Bind the ButtonRelease-1 event to the on_slider_xyz_button_release function
        self.slider_y.bind("<ButtonRelease-1>", self.on_slider_xyz_button_release)

        self.lb_y = Label(
            self.tip_y_frame, text=self.slider_y.get(), width=10, font=("Arial", 15)
        )
        self.lb_y.pack(pady=5)

        # TIP Z #########################
        self.slider_z = Scale(
            self.tip_z_frame,
            from_=0,
            to=up,
            orient=VERTICAL,
            length=slider_length,
            showvalue=True,
            resolution=resolution,
        )
        self.slider_z.pack(pady=5)

        # Bind the ButtonRelease-1 event to the on_slider_xyz_button_release function
        self.slider_z.bind("<ButtonRelease-1>", self.on_slider_xyz_button_release)

        self.lb_z = Label(
            self.tip_z_frame, text=self.slider_z.get(), width=10, font=("Arial", 15)
        )
        self.lb_z.pack(pady=5)

        self.send_adjust_to_esp()

    def send_adjust_to_esp(self):
        try:
            if callable(self.write_command):
                self.write_command("ADJUST")
            else:
                print("AdjustApp: write_command not set, skipping ADJUST")
        except Exception as e:
            print(f"AdjustApp: error sending ADJUST: {e}")

    def wrapper_return_to_main(self):
        self.is_active = False
        # Unbind Escape if it was bound on toplevel
        try:
            toplevel = self.frame.winfo_toplevel()
            toplevel.unbind_all("<Escape>")
        except Exception:
            try:
                self.master.unbind_all("<Escape>")
            except Exception:
                pass
        self.return_to_main()

    def on_slider_xyz_button_release(self, event):
        """Handles slider button release to update tip positions"""
        newx = self.slider_x.get()
        newy = self.slider_y.get()
        newz = self.slider_z.get()

        sendstring = f"TIP,{newx},{newy},{newz}"
        try:
            self.write_command(sendstring)
        except Exception as e:
            error_message = f"ERROR in set_tip_xxz {e}"
            messagebox.showerror("Error", error_message)

    def update_data(self, message):
        """Updates the Adjust interface with new data"""

        data = message.split(",")
        if data[0] == "ADJUST":
            # Update voltage label
            vf = float(data[1])
            v = format(vf, ".3f")
            self.voltage_label.config(text=v)

            # Update digits label
            nA = data[2].rjust(5, " ")
            digits = data[3].rjust(5, " ")
            display_str = f"{nA} [nA] {digits} [digits]"
            self.digits_label.config(text=display_str)

            # Update voltage progress bar
            self.voltage_progressbar["value"] = float(data[3])

    def destroy(self):
        """Destroys all widgets created by AdjustApp"""
        self.is_active = False
        self.voltage_frame.destroy()
        self.tip_frame.destroy()


class SinusApp:
    def __init__(self, master, write_command, return_to_main):
        # Initialize Sinus with callbacks and settings
        self.master = master
        self.write_command = write_command
        self.return_to_main = return_to_main
        self.is_active = True

        # Create a frame to hold the widgets
        self.frame = Frame(master)
        self.frame.pack(fill="both", expand=True)

        # Create a frame for the buttons
        self.button_frame = Frame(self.frame)
        self.button_frame.pack(fill="x", pady=10)

        # Create a Stop button to return to the main interface
        self.btn_stop = Button(
            self.button_frame, text="Stop", command=self.wrapper_return_to_main
        )
        self.btn_stop.pack(side="left", padx=10)

        # Create a label to display the sinus signal information
        self.label = tk.Label(self.frame, text="Sinus signal at ADC X, Y, Z")
        self.label.pack(pady=20)

    def wrapper_return_to_main(self):
        # Wrapper function to handle returning to the main interface
        self.is_active = False
        self.return_to_main()

    def request_sinus(self):
        self.write_command("SINUS")


class TunnelApp:
    def __init__(
        self, master, write_command, return_to_main, target_adc, tolerance_adc
    ):

        # Initialize TunnelApp with callbacks and settings
        self.master = master
        self.write_command = write_command
        self.return_to_main = return_to_main
        self.is_active = True
        self.target_adc = target_adc
        self.tolerance_adc = tolerance_adc

        # Create a frame to hold the widgets
        self.frame = Frame(master)
        self.frame.pack()

        # Create a frame for the buttons
        self.button_frame = Frame(self.frame)
        self.button_frame.pack(fill="x", pady=10)

        # Create a Back button to return to the main interface
        self.btn_back = Button(
            self.button_frame, text="Stop", command=self.wrapper_return_to_main
        )
        self.btn_back.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        # Create a Restart button to restart the TunnelApp
        self.btn_restart = Button(
            self.button_frame, text="Restart", command=self.restart
        )
        self.btn_restart.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Configure grid columns to center the buttons
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)

        # Initialize the plot
        self.tunnel_counts = float(
            config_utils.get_config("TUNNEL", "tunnelcounts", 200)
        )
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

        # Initialize data lists
        self.adc_data = []
        self.z_data = []
        self.colors = []

        # Start the measurement process with the read tunnelcounts value
        self.write_command(f"TUNNEL,{int(self.tunnel_counts)}")

    def update_adc_limits(self, target_adc, limit_adc):
        self.target_adc = target_adc
        self.limit_adc = limit_adc

    def wrapper_return_to_main(self):
        # Set is_active to False and return to the main interface
        self.is_active = False
        self.return_to_main()

    def restart(self):
        # Clear the plot data
        self.clear_plot_data()
        # Restart the TunnelApp
        self.frame.destroy()
        self.__init__(
            self.master,
            self.write_command,
            self.return_to_main,
            self.target_adc,
            self.tolerance_adc,
        )
        # print(f"Tolerance ADC: {self.tolerance_adc}")

    def clear_plot_data(self):
        # Clear the plot data
        self.adc_data = []
        self.z_data = []
        self.colors = []

    def update_data(self, message):
        if not hasattr(self, "adc_plot"):
            # Initialize plot elements
            (self.adc_plot,) = self.ax.plot([], [], "o", label="Tunnel")
            (self.z_plot,) = self.ax.plot([], [], "x", label="DAC Z")
            self.limit_hi_line = self.ax.axhline(
                y=self.target_adc + self.tolerance_adc,
                color="orange",
                linestyle="--",
                label="Limit hi",
            )
            self.limit_lo_line = self.ax.axhline(
                y=self.target_adc - self.tolerance_adc,
                color="orange",
                linestyle="--",
                label="Limit Lo",
            )

        # Update the plot with new data
        data = message.split(",")
        try:
            if data[0] == "TUNNEL":
                flag, adc, z = int(data[1]), int(data[2]), int(data[3])
            else:
                return False
        except Exception as e:
            print(f"Error: {e}, \n{message}")
            return False

        self.adc_data.append(adc)
        self.z_data.append(z)
        self.colors.append("red" if flag == 0 else "green")
        self.redraw_plot()

    def redraw_plot(self):
        # Clear the plot and redraw
        self.ax.clear()
        self.ax.scatter(
            range(len(self.adc_data)),
            self.adc_data,
            c=self.colors,
            marker="o",
            label="Tunnel",
        )
        self.ax.scatter(
            range(len(self.z_data)),
            self.z_data,
            c="black",
            marker="x",
            label="DAC Z",
        )
        self.ax.set_xlim(
            0, max(100, len(self.adc_data))
        )  # Adjust x-axis limit based on data length

        self.ax.axhline(
            y=self.target_adc + self.tolerance_adc,
            color="orange",
            linestyle="--",
            label="Limit hi",
        )
        self.ax.axhline(
            y=self.target_adc - self.tolerance_adc,
            color="orange",
            linestyle="--",
            label="Limit Lo",
        )
        self.ax.set_xlim(0, self.tunnel_counts)
        # self.ax.set_ylim(0, 0xFFFF)  # Adjust y-axis limit if needed
        self.ax.set_ylim(-0x8000, 0x7FFF)  # Set y-axis limit to int16_t range
        self.ax.set_xlabel("Counter")
        self.ax.set_ylabel("ADC and DAC Z")
        self.ax.set_title("Tunnel Current ADC and DAC Z")
        self.ax.legend()
        self.canvas.draw()
