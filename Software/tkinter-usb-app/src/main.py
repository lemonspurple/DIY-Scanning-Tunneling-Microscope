import atexit
import os
import sys
import time
from tkinter import Frame, Tk, messagebox, ttk

import com_port_utils  # Import the com_port_utils module
import config_utils
import usb_connection
from gui.app_manager import AppManager
from gui.menu import create_menu
from terminal import TerminalView

## Use fcntl over msvcrt if Linux is used
IS_WINDOWS = os.name == "nt"
if IS_WINDOWS:
    import msvcrt
else:
    import fcntl


# Define the global STATUS variable
STATUS = "INIT"

lock_handle = None
running = True


def prevent_multiple_instances():
    global lock_handle

    lock_file = (
        os.path.join(os.path.dirname(sys.executable), "app.lock")
        if hasattr(sys, "_MEIPASS")
        else os.path.join(os.path.dirname(__file__), "app.lock")
    )

    lock_handle = open(lock_file, "w")

    try:
        if IS_WINDOWS:
            msvcrt.locking(lock_handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("Another instance of the application is already running.")
        sys.exit(1)
    # Register a cleanup function to delete the lock file on exit
    atexit.register(delete_lock_file, lock_file)


def delete_lock_file(lock_file):
    global lock_handle
    try:
        if lock_handle:
            try:
                if IS_WINDOWS:
                    msvcrt.locking(lock_handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
            finally:
                lock_handle.close()
                lock_handle = None  # Set to None after closing

        if os.path.exists(lock_file):
            os.remove(lock_file)  # Delete the lock file

        print("Lock file deleted.")
    except Exception as e:
        print(f"Error deleting lock file: {e}")


def cleanup_tasks():
    global running, lock_handle
    running = False  # Signal the thread to stop
    print("Cleaning up tasks...")

    if lock_handle:  # Only unlock and close if not already handled
        try:
            if IS_WINDOWS:
                msvcrt.locking(lock_handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
        finally:
            lock_handle.close()
            lock_handle = None

    # esp_api_client.close_usb_connection()  # Uncommented to close USB connection


def global_on_close():
    print("on_close: Function triggered")
    try:
        esp_api_client.usb_conn.write_command("STOP")
    except Exception as e:
        print(f"Error sending STOP command: {e}")
    cleanup_tasks()
    root.destroy()


class MasterGui:
    def __init__(self, master):
        self.master = master
        self.master.title("500 EUR RTM - Connecting ...")
        self.master.geometry("900x600")

        # Use sys._MEIPASS to find the file in all environments
        if hasattr(sys, "_MEIPASS"):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)
        # Set the window icon

        icon_path = os.path.join(base_path, "assets", "icons", "stm_symbol.ico")

        try:
            self.master.iconbitmap(icon_path)
        except Exception as e:
            print(f"Icon not set (ignored): {e}")

        self.setup_gui_interface()
        # Initialize the USB connection handler
        self.initialize_usb_connection()

        # Initialize the idle_received attribute
        self.idle_received = False

        # Initialize the AdjustApp instance
        self.adjust_app = None

        # Initialize the ParameterApp instance
        self.parameter_app = None

        self.measure_app = None
        # Initialize optional app references to avoid AttributeError when
        # dispatch_received_data is called before those apps are opened.
        self.tunnel_app = None
        self.sinus_app = None
        self.target_adc = 0
        self.tolerance_adc = 0

    def initialize_usb_connection(self):
        # Initialize the USB connection handler
        self.usb_conn = usb_connection.USBConnection(
            update_terminal_callback=self.update_terminal,
            dispatcher_callback=self.dispatch_received_data,
        )
        # Provide the write_command callback to the terminal view if present
        try:
            if hasattr(self, "terminal_view"):
                self.terminal_view.set_write_command(self.usb_conn.write_command)
            if hasattr(self, "app_manager") and self.app_manager:
                self.app_manager.set_write_command(self.usb_conn.write_command)
        except Exception:
            pass

    def setup_gui_interface(self):
        # Create the menu bar (moved to gui/menu.py)
        callbacks = {
            "on_closing": self.on_closing,
            "open_measure": self.open_measure,
            "open_parameter": self.open_parameter,
            "open_adjust": self.open_adjust,
            "open_sinus": self.open_sinus,
            "open_tunnel": self.open_tunnel,
            "open_tunnel_simulate": self.open_tunnel_simulate,
            "open_measure_simulate": self.open_measure_simulate,
            "show_simulation_info": self.show_simulation_info,
        }
        self.menu_bar = create_menu(self.master, callbacks=callbacks)

        # Create a frame to hold the terminal and scrollbar, then instantiate TerminalView
        self.terminal_frame = Frame(self.master)
        # keep terminal area a fixed-ish width so app_frame displays correctly
        try:
            self.terminal_frame.config(width=300)
            self.terminal_frame.pack_propagate(False)
        except Exception:
            pass
        self.terminal_frame.pack(side="left", fill="y")
        self.terminal_view = TerminalView(self.terminal_frame)
        # Ensure the terminal_frame grid expands correctly
        try:
            self.terminal_frame.grid_rowconfigure(0, weight=1)
            self.terminal_frame.grid_columnconfigure(0, weight=1)
        except Exception:
            pass

        # Create the app manager which holds the right-side content
        self.app_manager = AppManager(
            master=self.master,
            write_command=None,
            return_to_main=self.return_to_main,
            disable_menu_cb=self.disable_menu,
            enable_menu_cb=self.enable_menu,
        )

    def connect(self):
        # Establish a connection to the selected COM port
        global STATUS

        self.usb_conn.port = config_utils.get_config("USB", "port")

        if not com_port_utils.is_com_port_available(self.usb_conn.port):
            self.update_terminal(f"COM port {self.usb_conn.port} is not available")
            return False
        if not self.usb_conn.establish_connection():
            self.update_terminal(f"COM port {self.usb_conn.port} cannot connect")
            return False

        self.usb_conn.start_receiving()
        try:
            self.usb_conn.write_command("STOP")
        except Exception as e:
            self.update_terminal(f"Error sending STOP command")
            return False
        self.idle_received = False  # Reset idle_received before waiting
        start_time = time.time()
        while not self.idle_received:
            self.master.update()
            time.sleep(0.1)
            if time.time() - start_time > 1:
                return False
        time.sleep(0.1)
        STATUS = "IDLE"
        return True

    def try_to_connect(self):
        # Try to establish a connection and select port if it fails
        result = self.connect()
        while not result:
            com_port_utils.select_port(self.master)
            if config_utils.get_config("USB", "port") == "None":
                self.master.destroy()
                return
            result = self.connect()

        # Update the window title with the COM port
        self.master.title(
            f"500 EUR RTM - {self.usb_conn.port} {self.usb_conn.baudrate} baud"
        )

        self.usb_conn.write_command("PARAMETER,?")

    def update_terminal(self, message):
        # Update the terminal with a new message
        try:
            if hasattr(self, "terminal_view"):
                self.terminal_view.update(message)
                try:
                    self.master.update_idletasks()
                except Exception:
                    pass
            else:
                # fallback: print to stdout
                print(message)
        except Exception as e:
            print(f"Error updating terminal: {e}")

    def dispatch_received_data(self, message):
        # Dispatch received data based on the current status
        global STATUS
        messages = message.split("\n")
        for msg in messages:
            ms = msg.split(",")
            messagetype = ms[0]
            if messagetype == "IDLE":
                self.idle_received = True
            if messagetype == "ADJUST":
                self.update_terminal(msg)
                adjust_app = None
                if hasattr(self, "app_manager") and self.app_manager:
                    adjust_app = self.app_manager.get_adjust_app()
                if adjust_app and getattr(adjust_app, "is_active", False):
                    adjust_app.update_data(msg)
            elif messagetype == "PARAMETER":
                self.update_terminal(msg)
                if ms[1] == "targetNa":
                    self.target_adc = self.calculate_adc_value(ms[2])
                if ms[1] == "toleranceNa":
                    self.tolerance_adc = self.calculate_adc_value(ms[2])
                parameter_app = None
                if hasattr(self, "app_manager") and self.app_manager:
                    parameter_app = self.app_manager.get_parameter_app()
                if parameter_app:
                    parameter_app.update_data(msg)
            elif messagetype == "TUNNEL":
                # Handle both "TUNNEL,DONE" and "TUNNEL,flag,adc,z" formats
                if len(ms) >= 2 and ms[1] == "DONE":
                    # Pass DONE message directly without conversion
                    self.update_terminal(msg)
                    tunnel_app = None
                    if hasattr(self, "app_manager") and self.app_manager:
                        tunnel_app = self.app_manager.get_tunnel_app()
                    if tunnel_app:
                        tunnel_app.update_data(msg)
                elif len(ms) >= 4:
                    # Handle data messages with flag, adc, z
                    adc_value = int(ms[2])
                    if (
                        adc_value > 0x7FFF
                    ):  # If greater than the max positive value for int16
                        adc_value -= 0x10000  # Convert to signed value
                    ms[2] = str(adc_value)
                    msg = ",".join(ms)

                    self.update_terminal(msg)
                    tunnel_app = None
                    if hasattr(self, "app_manager") and self.app_manager:
                        tunnel_app = self.app_manager.get_tunnel_app()
                    if tunnel_app:
                        tunnel_app.update_data(msg)
                else:
                    # Invalid TUNNEL message format
                    self.update_terminal(f"Invalid TUNNEL message: {msg}")
            elif messagetype == "FIND":
                self.update_terminal(msg)
            elif messagetype == "DATA":
                try:
                    if len(ms) == 2 and ms[1] == "DONE":
                        measure_app = None
                        if hasattr(self, "app_manager") and self.app_manager:
                            measure_app = self.app_manager.get_measure_app()
                        if measure_app:
                            measure_app.redraw_plot()
                        self.update_terminal("Measurement complete.")

                    # self.return_to_main()
                    if len(ms) == 4:
                        measure_app = None
                        if hasattr(self, "app_manager") and self.app_manager:
                            measure_app = self.app_manager.get_measure_app()
                        if measure_app:
                            measure_app.update_data(msg)

                    # Plot next set of data
                    if ms[1] == "0":
                        self.update_terminal(f"Processing Y {ms[2]}")
                except Exception as e:
                    self.update_terminal(f"Error measure: {msg}, \nError: {e}")

    def disable_menu(self):
        # Disable all menu points
        self.menu_bar.entryconfig("File", state="disabled")
        self.menu_bar.entryconfig("Measure", state="disabled")
        self.menu_bar.entryconfig("Settings", state="disabled")
        self.menu_bar.entryconfig("Tools", state="disabled")

    def enable_menu(self):
        # Enable all menu points
        self.menu_bar.entryconfig("File", state="normal")
        self.menu_bar.entryconfig("Measure", state="normal")
        self.menu_bar.entryconfig("Settings", state="normal")
        self.menu_bar.entryconfig("Tools", state="normal")

    def open_measure(self):
        # Open the MEASURE interface
        global STATUS
        STATUS = "MEASURE"
        # Delegate to AppManager
        if hasattr(self, "app_manager") and self.app_manager:
            self.app_manager.open_measure(simulate=False)

    def open_measure_simulate(self):
        # Open the MEASURE SIMULATE interface
        global STATUS
        STATUS = "MEASURE_SIMULATE"
        if hasattr(self, "app_manager") and self.app_manager:
            self.app_manager.open_measure(simulate=True)

    def open_tunnel(self):
        # self.usb_conn.write_command("PARAMETER,?")
        global STATUS
        STATUS = "TUNNEL"

        if hasattr(self, "app_manager") and self.app_manager:
            self.app_manager.target_adc = self.target_adc
            self.app_manager.tolerance_adc = self.tolerance_adc
            self.app_manager.open_tunnel(simulate=False)

    def open_tunnel_simulate(self):
        # Open the TUNNEL SIMULATE interface
        global STATUS
        STATUS = "TUNNEL_SIMULATE"

        if hasattr(self, "app_manager") and self.app_manager:
            self.app_manager.target_adc = self.target_adc
            self.app_manager.tolerance_adc = self.tolerance_adc
            self.app_manager.open_tunnel(simulate=True)

    def open_adjust(self):
        # Open the ADJUST interface
        global STATUS
        STATUS = "ADJUST"

        if hasattr(self, "app_manager") and self.app_manager:
            self.app_manager.open_adjust()

    def open_sinus(self):
        # Open the SINUS interface
        global STATUS
        STATUS = "SINUS"
        if hasattr(self, "app_manager") and self.app_manager:
            self.app_manager.open_sinus()

    def open_parameter(self):
        # Open the PARAMETER interface
        global STATUS
        STATUS = "PARAMETER"

        if hasattr(self, "app_manager") and self.app_manager:
            self.app_manager.set_write_command(self.usb_conn.write_command)
            self.app_manager.open_parameter()

    def return_to_main(self):
        # Send STOP and wait for an "IDLE" response before closing the app
        try:
            self.idle_received = False
            try:
                if hasattr(self, "usb_conn") and self.usb_conn:
                    self.usb_conn.write_command("STOP")
            except Exception:
                pass
        except Exception:
            pass

        # Wait for IDLE (set by dispatch_received_data) with timeout
        try:
            try:
                timeout = float(config_utils.get_config("GENERAL", "stop_timeout"))
            except Exception:
                timeout = 3.0
            start_time = time.time()
            while not self.idle_received:
                try:
                    self.master.update()
                except Exception:
                    pass
                time.sleep(0.05)
                if time.time() - start_time > timeout:
                    self.update_terminal("Timeout waiting for IDLE after STOP")
                    break
        except Exception:
            pass

        # Clear the app area via AppManager (remove widgets and clear references)
        try:
            if hasattr(self, "app_manager") and self.app_manager:
                self.app_manager._clear_app_frame()
                try:
                    self.app_manager.measure_app = None
                    self.app_manager.tunnel_app = None
                    self.app_manager.adjust_app = None
                    self.app_manager.sinus_app = None
                    self.app_manager.parameter_app = None
                except Exception:
                    pass
        except Exception:
            pass

        # Do NOT close the main window — just re-enable the menu and wait for user selection
        try:
            STATUS = "IDLE"
        except Exception:
            pass
        self.enable_menu()

    def create_main_interface(self):
        # Clear the existing interface

        for widget in self.master.winfo_children():
            widget.destroy()
        # Re-setup the interface without reinitializing the COM port
        self.setup_gui_interface()

    def open_settings(self):
        # Settings removed — kept for backward compatibility (no-op)
        pass

    def show_simulation_info(self):
        # Show information about simulation mode
        messagebox.showinfo(
            "Info Simulation",
            "Simulation means: There is a connection between Ouput 'DAC_Z' and Tunnel Input 'TUN'",
        )

    def on_closing(self):
        try:
            self.usb_conn.write_command("STOP")
        except:
            pass
        finally:
            self.close_usb_connection()
            self.master.destroy()

    def close_usb_connection(self):
        # Close the USB connection to free the COM port
        try:
            self.usb_conn.close_connection()
        except Exception as e:
            self.update_terminal(f"Error closing USB connection: {e}")

    def calculate_adc_value(self, nA):
        # Convert nA to float
        try:
            nA = float(nA)
        except ValueError:
            self.update_terminal(f"Invalid nA value: {nA}")
            return 0
        # Calculate adcValue using the formula
        adc_voltage_divider = float(
            config_utils.get_config("ADC_TO_NA", "adc_voltage_divider")
        )  # Use the utility function
        adc_value_max = float(
            config_utils.get_config("ADC_TO_NA", "adc_value_max")
        )  # Use the utility function
        adc_voltage_max = float(
            config_utils.get_config("ADC_TO_NA", "adc_voltage_max")
        )  # Use the utility function

        adc_value = (nA / adc_voltage_divider) * (adc_value_max / adc_voltage_max)
        adc_value = int(adc_value)  # Convert to integer
        return adc_value


if __name__ == "__main__":
    prevent_multiple_instances()

    root = Tk()
    style = ttk.Style(root)
    style.theme_use("default")  # Use a simple theme
    style.configure("Thin.Horizontal.TProgressbar", thickness=10)  # Set the thickness

    esp_api_client = MasterGui(root)

    print("Binding WM_DELETE_WINDOW to on_close")
    root.protocol("WM_DELETE_WINDOW", global_on_close)
    root.after(100, esp_api_client.try_to_connect)

    print("Program is running...")
    root.mainloop()
