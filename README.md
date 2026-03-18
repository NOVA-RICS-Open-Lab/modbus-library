<div  align="center"> 

# ModBus Library
[![License: MIT](https://img.shields.io/badge/License-MIT-red.svg)](https://opensource.org/licenses/MIT)

[Rodrigo Henriques](https://www.linkedin.com/in/rodrigoaghenriques/)<sup>1</sup>,
[Raúl Dinis](https://www.linkedin.com/in/raúl-mestre-dinis)<sup>1</sup>,
[André Rocha](https://scholar.google.pt/citations?user=k1GIyqcAAAAJ&hl=pt-PT)<sup>1</sup>

<sup>1</sup> **NOVA School of Science and Technology**,
and Associated Lab of Intelligent Systems (LASI), NOVA University
Lisbon, 2829-516 Lisbon, Portugal

<table>
  <tr>
    <td style="vertical-align: top;">
      This project focuses on developing a Python library designed to establish Modbus communication with an ESP microcontroller. The primary goal is to provide a robust software interface to control previously developed hardware: an interface board that handles signal conversion between industrial standards (24V) and the ESP (3.3V) found <a href="https://github.com/NOVA-RICS-Open-Lab/open-modular-controller">here</a>.
      By integrating this library, it becomes possible to read sensors and command industrial actuators remotely and in a standardized manner. This solution combines the versatility of Python with the reliability of the signal conditioning board, creating a complete, scalable automation system that is fully compatible with industry-standard protocols.
    </td>
    <td style="vertical-align: top;">
  </tr>
</table>

</div>

## <div align="center">Get Started</div>
Follow these steps to use this library:

1. **Prerequisite: Python**
   - Make sure you have Python 3.8 or higher installed on your system. You can check your version by running:
        - In Windows: ```python --version```
        - In MacOs or Linux: ```python3 --version```
2. **Install via pip**
   - Download everything found [here](./src/libs/).
   - Open the directory in your cmd and run ```pip install .```
   - If you've changed anything in the library after installing it run ```pip install . --upgrade``` in the respective directory to update it.
3. **Configure the ESP**
   - Download the provided code found in [here](./tests/Esp/Esp.ino).
   - Choose one of two ways to configure the IP address:
     - Connect the ESP to your wifi and go to the router settings to see in wich IP the ESP has connected.
     - Introduce in the ESP code the IP address you want to conncect.
   - Upload the provided code in your ESP.
4. **Test the library**
   - Download the provided code found in [here](./tests/).
   - Connect your PC to the IP address where your ESP is conncected.

If all tests passed you are ready to use this library.

---

### Usage instructions
Once your ESP and Library setup is complete, you can begin using the device. The ESP manages the input and output for each control pin, with a standard operating voltage of 24V. Please note:

- **Control Limitations**: These pins are designed for control signals only. Avoid applying high current loads to prevent damage.
- **Testing & Example Code**: Refer to the [tests](./tests/) folder for use case examples and tests.

Follow these guidelines, and your project should operate as expected!

---

### Project Structure
For you to better understand this repository organization here is a quick overview of its structure and where to find what you might be looking for:
```
modbus-library
├── docs                          # documentation assets
├── src                           # evaluation code
│   └── libs                      # developed libraries
│       ├── esp32_Modbus          # modbus TCP controller library
│       │   ├── __init__.py       # initialize library code
│       │   └── client_esp32.py   # library code
│       └── pyproject.toml        # configuration and Metadata
└── tests                         # use case example scripts
    ├──Esp                        # folder with esp code
    │   └── Esp.ino               # esp code
    ├── ciclo_producao.py         # library test 1
    └── clientEsp32_Test.py       # library test 2
```
## <div align="center">Documentation</div>
Functions included in this library:

1. **ESP32Controller class**
   - connect(self):
     - Establishes the Modbus TCP connection with the ESP32 device.
   - disconnect(self):
     - Stops the reading loops and closes the Modbus client connection.
   - _notification_loop(self):
     - Background thread that monitors for data changes and triggers the callback if enabled.
   - sync_all(self):
     - Synchronizes all sensor and actuator registers by reading them directly from the device.
   - write_direct_register(self, address, value):
     - Writes a specific value to a Modbus holding register address.  
        address: Integer - The specific register address on the ESP32.  
        value: Integer - The value to be written to the register.
   - _read_loop(self):
     - Main monitoring loop that checks for sensor changes and handles the notification flag
2. **ModbusMonitorUI class**
   - start_ui(self):
     - Sets up the main window, scrollable canvas, and starts the Tkinter main loop.
   - on_close(self):
     - Handles safe termination of the UI window and its update loop.
   - setup_device_list(self):
     - Dynamically creates UI components (labels and status LEDs) for each device in the manager.
   - update_loop(self):
     - Periodic UI update function that refreshes sensor values and actuator visual states.
3. **MultiESP32Manager class**
   - open_ui(self):
     - Launches the ModbusMonitorUI in a separate daemon thread.
   - connect_and_monitor(self):
     - Connects to all devices and starts their respective background reading loops.
   - get_individual_sensors(self, device_name):
     - Retrieves the sensor states for a specific device, mapped to their global IDs.  
       device_name: String - The name of the device (as defined in initialization).
   - get_individual_actuators(self, device_name):
     - Retrieves the actuator states for a specific device mapped to global IDs.  
       device_name: String - The name of the device.
   - enable_general_sub(self):
     - Enables notification callbacks for every managed device.
   - enable_exclusive_sub(self, device_name):
     - Enables notifications for a specific device while disabling all others.  
       device_name: String - The name of the device to keep active.
   - disable_all_subs(self):
     - Disables notification callbacks for all managed devices.
   - get_global_sensors(self):
     - Returns a sorted dictionary of all sensors across all devices using global IDs.
   - get_global_actuators(self):
     - Returns a sorted dictionary of all actuators across all devices using global IDs.
   - set_global_actuator(self, global_id, state):
     - Updates the state of an actuator using its unique global ID.  
       global_id: Integer - The unique global ID assigned to the actuator.  
       state: Integer - The value (e.g., 0 or 1) to set.
   - set_individual_actuator(self, device_name, local_id, state):
     - Updates a specific actuator on a named device using its local ID.  
       device_name: String - The name of the device.
       local_id: Integer - The ID (1-7) of the actuator on that board.
       state: Integer - The value to set.
   - disconnect_all(self):
     - Properly disconnects all ESP32 devices and stops all monitoring threads.

> **Note**: This work was originally developed for the ESP32 platform, taking advantage of its performance and integrated connectivity. However, the solution is highly versatile and can be adapted to any other microcontroller, provided it meets two fundamental requirements: Wi-Fi connectivity and the ability to communicate via the Modbus protocol. Consequently, the project remains hardware-agnostic, allowing for implementation across various architectures that support these networking and industrial communication standards.

## <div align="center">Contribution Guidelines</div>
NOVA RICS Open Lab open source, and we welcome contributions from the community! See the [Contribution](CONTRIBUTING.md) guide for more information on the development workflow and the internals of the wandb library. For project related bugs and feature requests, visit [GitHub Issues](https://github.com/NOVA-RICS-Open-Lab/modbus-library/issues) or contact novaricsopenlab@gmail.com

## <div align="center">License</div>
This repository is released under the MIT License. Please see the [LICENSE](LICENSE) file for more details.

## <div align="center">Contacts</div>
For any questions regarding this or any other project please contact us at novaricsopenlab@gmail.com, contact the developer ra.henriques@campus.fct.unl.pt or enroll in our [Discussion Forum](https://github.com/NOVA-RICS-Open-Lab/modbus-library/discussions) for sharing your ideas and sharing projects
