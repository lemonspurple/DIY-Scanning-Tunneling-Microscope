import os
from datetime import datetime
from tkinter import Button, Frame

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm  # Import colormap utilities
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class MeasureApp:
    def __init__(self, master, write_command, return_to_main, simulate=False):
        # Initialize MeasureApp with callbacks and settings
        self.master = master
        self.write_command = write_command
        self.return_to_main = return_to_main
        self.is_active = True
        self.simulate = simulate

        # Create a frame to hold the widgets
        self.frame = Frame(master)
        self.frame.pack()

        # Create a Back button to return to the main interface
        self.btn_back = Button(
            self.frame, text="Stop - ESC", command=self.wrapper_return_to_main
        )
        self.btn_back.pack(pady=10)

        # Create a Reset Rotation button to reset the 3D plot rotation
        self.btn_reset_rotation = Button(
            self.frame, text="Reset Rotation", command=self.reset_rotation
        )
        self.btn_reset_rotation.pack(pady=10)
        self.btn_reset_rotation.pack_forget()  # Initially hide the Reset Rotation button

        # Initialize the 3D plot
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection="3d")
        self.x_data = []
        self.y_data = []
        self.z_data = []

        # Store the initial rotation state
        self.initial_elev = self.ax.elev
        self.initial_azim = self.ax.azim

        # Embed the plot in a Tkinter canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        self.canvas.mpl_connect(
            "motion_notify_event", self.on_plot_hover
        )  # Connect the hover event
        self.redraw_plot()

        # Start the measurement process (only if write_command is callable)
        try:
            cmd = "MEASURE SIMULATE" if self.simulate else "MEASURE"
            if callable(self.write_command):
                self.write_command(cmd)
            else:
                print(f"MeasureApp: write_command not set, skipping send: {cmd}")
        except Exception as e:
            print(f"MeasureApp: error sending command '{cmd}': {e}")

        # Create the measurements folder if it doesn't exist
        measurements_folder = os.path.join(os.getcwd(), "measurements")
        os.makedirs(measurements_folder, exist_ok=True)

        # Generate a filename based on the current date and time
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.measurement_file_path = os.path.join(
            measurements_folder, f"measurement_{timestamp}.csv"
        )

        # Bind the Escape key on the toplevel so it can be unbound cleanly
        try:
            toplevel = self.frame.winfo_toplevel()
            toplevel.bind_all("<Escape>", lambda event: self.wrapper_return_to_main())
        except Exception:
            try:
                self.master.bind_all(
                    "<Escape>", lambda event: self.wrapper_return_to_main()
                )
            except Exception:
                pass

    def wrapper_return_to_main(self):
        # Set is_active to False and return to the main interface
        self.is_active = False
        # Unbind escape handler to avoid leaking handlers
        try:
            toplevel = self.frame.winfo_toplevel()
            toplevel.unbind_all("<Escape>")
        except Exception:
            try:
                self.master.unbind_all("<Escape>")
            except Exception:
                pass
        self.return_to_main()

    def update_data(self, message):
        # Safety check to ensure the object is still active
        if not hasattr(self, "is_active") or not self.is_active:
            return False

        # Update the Parameter interface with new data
        data = message.split(",")

        # Handle DONE message
        if len(data) > 1 and data[1] == "DONE":
            print("Measurement completed")
            self.wrapper_return_to_main()
            return True

        try:
            x, y, z = int(data[1]), int(data[2]), int(data[3])
        except (IndexError, ValueError) as e:
            print(f"Error parsing data: {e}, \n{message}")
            return False

        # Append the data to the file
        with open(self.measurement_file_path, "a") as file:
            file.write(f"{x},{y},{z}\n")

        # Update the plot
        self.x_data.append(x)
        self.y_data.append(y)
        self.z_data.append(z)

        if x == 0:
            self.redraw_plot()

    def redraw_plot(self):
        # Safety check to ensure the object is still active and has required attributes
        if not hasattr(self, "is_active") or not self.is_active:
            return
        if not hasattr(self, "ax") or not hasattr(self, "canvas"):
            return

        # Clear the plot and redraw
        self.ax.clear()
        self.ax.set_xlim(0, 200)
        self.ax.set_ylim(0, 200)
        self.ax.set_zlim(0, 0xFFFF)

        # Check if there is enough data to create a surface
        if len(self.x_data) > 2 and len(self.y_data) > 2 and len(self.z_data) > 2:
            # Prepare data for the 3D plot
            x = np.array(self.x_data)
            y = np.array(self.y_data)
            z = np.array(self.z_data)

            # Plot the triangular surface with the new data
            self.ax.plot_trisurf(x, y, z, cmap=cm.coolwarm, linewidth=0.2)

        # Redraw the canvas and flush the events to update the display
        self.canvas.draw()
        self.canvas.flush_events()

    def reset_rotation(self):
        # Reset the rotation of the 3D plot to its initial state
        self.ax.view_init(
            elev=self.initial_elev, azim=self.initial_azim
        )  # Reset to initial elevation and azimuthal angles
        self.canvas.draw()
        self.btn_reset_rotation.pack_forget()  # Hide the Reset Rotation button after resetting

    def on_plot_hover(self, event):
        # Show the Reset Rotation button only if the plot has been rotated
        if self.ax.elev != self.initial_elev or self.ax.azim != self.initial_azim:
            self.btn_reset_rotation.pack(pady=10)
