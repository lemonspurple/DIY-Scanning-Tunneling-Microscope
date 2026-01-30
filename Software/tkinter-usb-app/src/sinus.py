import tkinter as tk
from tkinter import Button, Frame


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
        # Unbind Escape handler if bound on toplevel
        try:
            toplevel = self.frame.winfo_toplevel()
            toplevel.unbind_all("<Escape>")
        except Exception:
            try:
                self.master.unbind_all("<Escape>")
            except Exception:
                pass
        self.return_to_main()

    def request_sinus(self):
        try:
            if callable(self.write_command):
                self.write_command("SINUS")
            else:
                print("SinusApp: write_command not set, skipping SINUS")
        except Exception as e:
            print(f"SinusApp: error sending SINUS: {e}")
