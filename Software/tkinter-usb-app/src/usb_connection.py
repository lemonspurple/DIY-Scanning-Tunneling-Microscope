import queue
import threading
import time

import serial
import serial.tools.list_ports
from serial import SerialException

import config_utils


class USBConnection:
    def __init__(self, update_terminal_callback, dispatcher_callback):
        # Initialize USBConnection with callbacks and settings
        self.update_terminal = update_terminal_callback
        self.dispatcher_callback = dispatcher_callback
        self.connection = None
        self.is_connected = False
        self.connection_established = False
        self.data_queue = queue.Queue()
        self.esp_to_queue = None
        self.waiting_for_idle = False
        self.running = False
        self.receive_running = False
        self.port = config_utils.get_config("USB", "port")
        self.baudrate = config_utils.get_config("USB", "baudrate") or 460800

    def establish_connection(self):
        try:
            self.connection = serial.Serial(
                self.port, self.baudrate, timeout=1, write_timeout=1
            )
            self.is_connected = True
            return True
        except serial.SerialTimeoutException as e:
            self.is_connected = False
            error_msg = f"Connection timeout on port {self.port}: {e}"
            self.update_terminal(error_msg)
            print(f"ERROR establish_connection timeout: {error_msg}")
            return False
        except SerialException as e:
            self.is_connected = False
            error_msg = f"Serial connection error on port {self.port}: {e}"
            self.update_terminal(error_msg)
            print(f"ERROR establish_connection: {error_msg}")
            return False
        except Exception as e:
            self.is_connected = False
            error_msg = f"Unexpected error connecting to {self.port}: {e}"
            self.update_terminal(error_msg)
            print(f"ERROR establish_connection unexpected: {error_msg}")
            return False

    def esp_restart(self):
        # Send a restart command (Ctrl+C) to the ESP device
        if self.is_connected:
            self.connection.write("STOP")

    def start_receiving(self):
        if self.is_connected:
            self.start_esp_to_queue()
            self.start_read_queue()
            return True
        else:
            return False

    def write_command(self, command):
        # Write a command to the ESP device
        if self.is_connected:
            try:
                self.connection.write((command + "\n").encode())
                self.update_terminal(f"To STM: {command}")
            except serial.SerialTimeoutException as e:
                self.update_terminal(f"Timeout error sending command: {e}")
                print(f"ERROR write_command timeout {e}")
            except SerialException as e:
                self.update_terminal(f"Error sending command: {e}")
                print(f"ERROR write_command {e}")
        else:
            self.update_terminal("Not connected to any device.")
            print("ERROR write_command")

    # Consume queue
    def start_read_queue(self):
        # Start a background thread to read the data queue
        self.reading_thread = threading.Thread(target=self.read_queue_loop, daemon=True)
        self.running = True
        self.reading_thread.start()

    def read_queue_loop(self):
        # Loop to read messages from the data queue and dispatch them
        global STATUS
        buffer = ""
        while self.running:
            while not self.data_queue.empty():
                buffer += (
                    self.data_queue.get() + "\n"
                )  # Add newline to simulate complete lines
                lines = buffer.split("\n")
                buffer = lines.pop()  # Keep the last partial line in the buffer

                if lines:
                    self.dispatcher_callback("\n".join(lines))
            time.sleep(0.00001)

    def stop_read_queue(self):
        # Stop the read queue loop
        self.running = False

    def queue_is_empty(self):
        # Check if the data queue is empty
        return self.data_queue.empty()

    # ESP to queue
    def start_esp_to_queue(self):
        # Start the ESP to queue thread
        self.receive_running = True
        threading.Thread(target=self.esp_to_queue_loop, daemon=True).start()

    def esp_to_queue_loop(self):
        # Loop to read responses from the ESP device and put them in the data queue
        buffer = ""
        while self.receive_running:
            try:
                # Read available data from the serial port
                if self.connection.in_waiting > 0:
                    buffer += self.connection.read(self.connection.in_waiting).decode()
                    lines = buffer.split("\n")
                    buffer = lines.pop()  # Keep the last partial line in the buffer

                    for line in lines:
                        if line.strip():
                            self.data_queue.put(line.strip())
            except Exception as e:
                print(f"Error in esp_to_queue: {e}")
                self.receive_running = False
                raise

    def stop_esp_to_queue(self):
        # Stop the ESP to queue loop
        self.receive_running = False

    def close_connection(self):
        # Close the USB connection and stop all threads
        self.stop_read_queue()
        self.stop_esp_to_queue()
        if self.connection and self.connection.is_open:
            self.connection.close()
        self.is_connected = False
        self.connection_established = False
