# Tkinter USB App 500 EUR RTM

With this app, the 500 EUR RTM is controlled via USB.


## Setup Instructions

1. Clone the repository into folder 500_RTM:
   ```
   cd 500_RTM
   git clone https://github.com/PeterDirnhofer/tkinter-usb-app.git
   ```


2. Create and activate a virtual environment named .venv:
   **On Windows:**
   ```sh
   cd tkinter-usb-app
   python -m venv .venv
   .venv\Scripts\activate
   ```

   **On Debian/Ubuntu based Linux**
   ```
   sudo apt install python3.12-venv
   cd tkinter-usb-app
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   **On macOS/Linux:**
   ```sh
   cd tkinter-usb-app
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the required dependencies (make sure your environment is activated):
   ```sh
   pip install -r requirements.txt
   ```

   **On Debian/Ubuntu based Linux**
   ```
   sudo apt install python3-pip
   pip install -r requirements.txt
   ```

## Run the Project in Visual Studio Code

   **On Linux**
   You'll get the following error if your user account lacks the permissions.
   ```
   COM port None is not available
   Try to connect /dev/ttyUSB0...
   Serial connection error on port /dev/ttyUSB0: [Errno 13] Permission denied: '/dev/ttyUSB0'
   Could not open port /dev/ttyUSB0: [Errno 13] Permission denied: '/dev/ttyUSB0'
   COM port /dev/ttyUSB0 cannot connect
   ```

   Therefore use the following command:
   ```
   sudo usermod -aG dialout $USER
   ```

   IMPORTANT: Change will take effect after reboot.

### Open the Project in Visual Studio Code

From your project directory, open the `tkinter-usb-app` folder in Visual Studio Code by running:
(You may be required to install the Python extension to run it)

```sh
cd tkinter-usb-app
code .
```

> **Note:** Be sure to use `code .` (with the dot) to open the current folder in VS Code. Using only `code` will not open the folder as a project.

## Run the Program

Select `main.py` in `src` folder . Click the **Run** button (Run Python File) to start the application.

## Usage Guidelines

- When you start the application, it will automatically attempt to establish a USB connection with the ESP32 device.
- If the connection is successful and the ESP32 responds with **"IDLE"**, you can select from the following main functionalities:
   - **Measure:** Perform measurement tasks and view real-time data from the device.
   - **Parameter:** Access controls for adjusting device parameters as needed.
   - **Tools:** Access additional utilities for device management and diagnostics, such as:
      - Manually set Hardware DACs and read ADC
      - Make DACs to output a sinus
      - **Init Tunnel Current:** Set DAC Z to establish  tunnel contact.
      - **Show Measurement During Tunnel Contact:** Display real-time measurement data as the device establishes tunnel contact.



## License

This project is licensed under the MIT License. See the LICENSE file for more details.
