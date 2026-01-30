import os
import sys
from tkinter import Button, Frame

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import config_utils


class TunnelApp:
    def __init__(
        self,
        master,
        write_command,
        return_to_main,
        target_adc,
        tolerance_adc,
        simulate=False,
    ):

        # Initialize TunnelApp with callbacks and settings
        self.master = master
        self.write_command = write_command
        self.return_to_main = return_to_main
        self.is_active = True
        self.target_adc = target_adc
        self.tolerance_adc = tolerance_adc
        self.simulate = simulate

        # Create a frame to hold the widgets
        self.frame = Frame(master)
        self.frame.pack()

        # Create a frame for the buttons
        self.button_frame = Frame(self.frame)
        self.button_frame.pack(fill="x", pady=10)

        # Create a Back button to return to the main interface
        self.btn_back = Button(
            self.button_frame, text="STOP - ESC", command=self.wrapper_return_to_main
        )
        self.btn_back.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Add a Freeze button to toggle the restart loop
        self.btn_freeze = Button(
            self.button_frame, text="Stop", command=self.toggle_freeze
        )
        self.btn_freeze.grid(row=0, column=1, padx=10, pady=10, sticky="e")

        # Initialize the freeze state
        self.is_frozen = False
        self.after_id = None

        # Bind the Escape key globally to the wrapper_return_to_main method
        try:
            toplevel = self.frame.winfo_toplevel()
            toplevel.bind_all("<Escape>", lambda event: self.wrapper_return_to_main())
        except Exception:
            # Fallback to master if toplevel binding fails
            try:
                self.master.bind_all(
                    "<Escape>", lambda event: self.wrapper_return_to_main()
                )
            except Exception:
                pass

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
        cmd = (
            f"TUNNEL SIMULATE,{int(abs(self.tunnel_counts))}"
            if self.simulate
            else f"TUNNEL,{int(abs(self.tunnel_counts))}"
        )
        try:
            if callable(self.write_command):
                self.write_command(cmd)
            else:
                print(f"TunnelApp: write_command not set, skipping send: {cmd}")
        except Exception as e:
            print(f"TunnelApp: error sending command '{cmd}': {e}")

    def update_adc_limits(self, target_adc, limit_adc):
        self.target_adc = target_adc
        self.limit_adc = limit_adc

    def wrapper_return_to_main(self):
        # Set is_active to False and return to the main interface
        self.is_active = False
        # Unbind the Escape handler to avoid leaking handlers
        try:
            toplevel = self.frame.winfo_toplevel()
            toplevel.unbind_all("<Escape>")
        except Exception:
            try:
                self.master.unbind_all("<Escape>")
            except Exception:
                pass
        self.return_to_main()

    def restart(self):
        # Clear the plot data
        self.clear_plot_data()
        # Restart the TunnelApp
        # Destroy existing UI and recreate the TunnelApp instance in-place.
        try:
            self.frame.destroy()
        except Exception:
            pass
        try:
            # Re-initialize the object safely; write_command may be None.
            self.__init__(
                self.master,
                self.write_command,
                self.return_to_main,
                self.target_adc,
                self.tolerance_adc,
                self.simulate,
            )
        except Exception as e:
            print(f"TunnelApp.restart: failed to reinitialize TunnelApp: {e}")

    def clear_plot_data(self):
        # Clear the plot data
        self.adc_data = []
        self.z_data = []
        self.colors = []

    def toggle_freeze(self):
        # Toggle the freeze state
        self.is_frozen = not self.is_frozen
        print(f"Freeze state toggled. is_frozen: {self.is_frozen}")  # Debugging
        if self.is_frozen:
            self.btn_freeze.config(text="Run")
            # Cancel the scheduled restart if it exists
            if self.after_id is not None:
                self.master.after_cancel(self.after_id)
                self.after_id = None  # Reset the after_id
            # Show the "STOP - ESC" button when the loop is stopped
            self.btn_back.grid()
        else:
            self.btn_freeze.config(text="Stop")
            # Hide the "STOP - ESC" button while the loop is running
            self.btn_back.grid_remove()
            # Restart the loop when unfreezing
            self.restart()

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
                if len(data) >= 2 and data[1] == "DONE":
                    # End of data reached
                    self.redraw_plot()
                    self.is_active = False  # Stop the tunnel loop

                    # Wait for 500ms, then restart the tunnel loop if not frozen
                    if not self.is_frozen:  # Check if the loop is frozen
                        print("Restarting tunnel loop...")  # Debugging
                        self.after_id = self.master.after(500, self.restart)
                    else:
                        print("Tunnel loop is frozen. Restart skipped.")  # Debugging
                        # Show the "STOP - ESC" button only when the loop is stopped
                        self.btn_back.grid()
                        self.btn_freeze.config(text="Run")
                    return True

                elif len(data) >= 4:
                    flag, adc, z = int(data[1]), int(data[2]), int(data[3])

                    if flag == 0:  # Data out of limits
                        self.adc_data.append(adc)
                        self.z_data.append(z)
                        self.colors.append("red")
                    elif flag == 1:  # Data within limits
                        self.adc_data.append(adc)
                        self.z_data.append(z)
                        self.colors.append("green")
                else:
                    return False
            else:
                return False
        except Exception as e:
            print(f"Error: {e}, \n{message}")
            return False

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
        self.ax.set_ylim(-1000, 0xFFFF)  # Set y-axis limit to int16_t range
        self.ax.set_xlabel("Counter")
        self.ax.set_ylabel("ADC and DAC Z")
        self.ax.set_title("Tunnel Current ADC and DAC Z")
        self.ax.legend()

        # Adjust margins
        self.fig.subplots_adjust(left=0.2, right=0.95, top=0.9, bottom=0.1)

        # Redraw the canvas
        self.canvas.draw()
