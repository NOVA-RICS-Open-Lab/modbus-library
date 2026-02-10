from pymodbus.client import ModbusTcpClient
import threading
import time
import tkinter as tk
from tkinter import ttk

class ESP32Controller:
    """
    Handles individual ESP32 communication via Modbus TCP.
    Manages connection, sensor polling and actuator control.
    """
    def __init__(self, name, ip, port, offset_id, callback):
        """
        Initializes network settings, internal state dictionaries, and thread locks.
        
        :param name: String - Unique identifier for this ESP32 unit.
        :param ip: String - The IP address of the ESP32.
        :param port: Integer - The TCP port for Modbus (usually 502 or 8009).
        :param offset_id: Integer - Starting number used to calculate global IDs.
        :param callback: Function - The function to call when a sensor value changes.
        """
        self.name = name
        self.ip = ip
        self.port = port
        self.offset_id = offset_id 
        self.callback = callback  
        self.client = ModbusTcpClient(self.ip, port=self.port, timeout=5)
        self.lock = threading.Lock()
        
        self.sensors = {f's{i}': 0 for i in range(1, 8)}
        self.actuators = {f'a{i}': 0 for i in range(1, 8)}
        self.running = False
        
        self.change_event = threading.Event()
        self.notifications_enabled = False
        self._actuator_map = {i: 500 + (i-1) for i in range(1, 8)}

    def connect(self):
        """Establishes the Modbus TCP connection with the ESP32 device."""
        return self.client.connect()

    def disconnect(self):
        """Stops the reading loops and closes the Modbus client connection."""
        self.running = False
        self.client.close()

    def _notification_loop(self):
        """Background thread that monitors for data changes and triggers the callback if enabled."""
        while self.running:
            if self.change_event.wait(timeout=0.5):
                if self.notifications_enabled and self.callback:
                    self.callback(self.name, self.sensors, self.offset_id)
                self.change_event.clear()

    def sync_all(self):
        """Synchronizes all sensor and actuator registers by reading them directly from the device."""
        with self.lock:
            if not self.client.connected: self.client.connect()
            res_s = self.client.read_input_registers(300, count=7)
            if not res_s.isError():
                for i in range(7): self.sensors[f's{i+1}'] = res_s.registers[i]
            
            res_a = self.client.read_holding_registers(500, count=7)
            if not res_a.isError():
                for i in range(7): self.actuators[f'a{i+1}'] = res_a.registers[i]

    def write_direct_register(self, address, value):
        """
        Writes a specific value to a Modbus holding register address.
        
        :param address: Integer - The specific register address on the ESP32.
        :param value: Integer - The value to be written to the register.
        """
        with self.lock:
            if not self.client.connected: self.client.connect()
            result = self.client.write_register(address, value)
            return not result.isError()
        
    def _read_loop(self):
        """Main monitoring loop that checks for sensor changes and handles the notification flag (register 400)."""
        self.running = True
        threading.Thread(target=self._notification_loop, daemon=True).start()
        
        last_sync = time.time()
        while self.running:
            try:
                if time.time() - last_sync > 5:
                    self.sync_all()
                    last_sync = time.time()

                if not self.client.connected: self.client.connect()
                with self.lock:
                    flag_read = self.client.read_holding_registers(400, count=1)
                    if not flag_read.isError() and flag_read.registers[0] != 0:
                        flag = flag_read.registers[0]
                        res = self.client.read_input_registers(flag, count=1)
                        if not res.isError():
                            val = res.registers[0]
                            key = f's{flag-299}'
                            if self.sensors[key] != val:
                                self.sensors[key] = val
                                self.change_event.set()
                            self.client.write_register(400, 0)
            except:
                pass
            time.sleep(0.2)

class ModbusMonitorUI:
    """
    Tkinter-based Graphical User Interface for real-time monitoring of all managed ESP32 devices.
    """
    def __init__(self, manager):
        """
        Initializes the UI with a reference to the MultiESP32Manager.
        
        :param manager: MultiESP32Manager - The manager instance containing the devices to monitor.
        """
        self.manager = manager
        self.root = None
        self.device_widgets = {}
        self.is_running = False

    def start_ui(self):
        """Sets up the main window, scrollable canvas, and starts the Tkinter main loop."""
        self.is_running = True
        self.root = tk.Tk()
        self.root.title("Monitor ESP32 Modbus")
        self.root.geometry("950x600")

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        main_canvas = tk.Canvas(self.root, bg="#f0f0f0")
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        self.scroll_frame = tk.Frame(main_canvas, bg="#f0f0f0")
        self.scroll_frame.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
        main_canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.setup_device_list()
        self.update_loop()
        self.root.mainloop()

    def on_close(self):
        """Handles safe termination of the UI window and its update loop."""
        self.is_running = False
        if self.root:
            self.root.quit()

            try:
                self.root.update() 
                self.root.destroy()
            except:
                pass
            self.root = None

    def setup_device_list(self):
        """Dynamically creates UI components (labels and status LEDs) for each device in the manager."""
        for name, device in self.manager.devices.items():
            dev_frame = tk.LabelFrame(self.scroll_frame, text=f" ESP32: {name} ", font=('Arial', 10, 'bold'))
            dev_frame.pack(fill="x", padx=10, pady=10)
            self.device_widgets[name] = {'sensors': {}, 'actuators': {}}

            s_wrap = tk.Frame(dev_frame)
            s_wrap.pack(fill="x", pady=5)
            for i in range(1, 8):
                f = tk.Frame(s_wrap)
                f.pack(side="left", padx=8)
                tk.Label(f, text=f"S{i}").pack()
                lbl = tk.Label(f, text="0", bg="#eeeeee", width=6, relief="sunken")
                lbl.pack()
                self.device_widgets[name]['sensors'][f's{i}'] = lbl

            a_wrap = tk.Frame(dev_frame) 
            a_wrap.pack(fill="x", pady=5)
            for i in range(1, 8):
                f = tk.Frame(a_wrap)
                f.pack(side="left", padx=8)
                tk.Label(f, text=f"A{i}").pack()
                led = tk.Label(f, text="OFF", bg="#444444", fg="white", width=6)
                led.pack()
                self.device_widgets[name]['actuators'][f'a{i}'] = led

    def update_loop(self):
        """Periodic UI update function that refreshes sensor values and actuator visual states."""
        if not self.is_running or self.root is None:
            return
        try:
            if not self.root.winfo_exists():
                return
            for name, device in self.manager.devices.items():
                if name not in self.device_widgets: continue
                
                for k, lbl in self.device_widgets[name]['sensors'].items():
                    v = device.sensors.get(k, 0)
                    if lbl.winfo_exists():
                        lbl.config(text=str(v), bg="#d1ffd1" if v > 0 else "#eeeeee")
                
                for k, led in self.device_widgets[name]['actuators'].items():
                    s = device.actuators.get(k, 0)
                    if led.winfo_exists():
                        led.config(text="ON" if s > 0 else "OFF", bg="#ff4444" if s > 0 else "#444444")
            
            if self.is_running and self.root:
                self.root.after(300, self.update_loop)
        except (tk.TclError, RuntimeError):
            self.is_running = False

class MultiESP32Manager:
    """
    High-level manager for multiple ESP32 controllers. Facilitates global ID mapping,
    batch connections, and provides an API for sensor/actuator interaction.
    """
    def __init__(self, configurations, callback_function):
        """
        Initializes the manager, creates device instances, and maps local sensors to a global ID space.
        
        :param configurations: List of Dicts - e.g., [{'name': 'ESP1', 'ip': '192.168.1.10'}, ...]
        :param callback_function: Function - Shared callback to trigger when any device changes state.
        """
        self.devices = {}
        self.global_map = {} 
        self.default_port = 8009
        self._ui_instance = None
        
        for i, dev in enumerate(configurations):
            name = dev['name']
            ip = dev['ip']
            offset = i * 7
            esp_obj = ESP32Controller(name, ip, self.default_port, offset, callback_function)
            self.devices[name] = esp_obj
            for n in range(1, 8):
                self.global_map[n + offset] = {'obj': esp_obj, 'local_id': n}

    def open_ui(self):
        """Launches the ModbusMonitorUI in a separate daemon thread."""
        if self._ui_instance and self._ui_instance.is_running:
            return False
            
        def run_ui():
            ui = ModbusMonitorUI(self)
            self._ui_instance = ui 
            try:
                ui.start_ui()
            except Exception as e:
                print(f"\n[UI Error]: {e}")
            finally:
                ui.is_running = False
                self._ui_instance = None

        ui_thread = threading.Thread(target=run_ui, daemon=True)
        ui_thread.start()
        return True

    def connect_and_monitor(self):
        """Connects to all devices and starts their respective background reading loops."""
        results = {}
        for name, esp in self.devices.items():
            success = esp.connect()
            results[name] = success
            if success:
                esp.sync_all()
                threading.Thread(target=esp._read_loop, daemon=True).start()
        return results

    def get_individual_sensors(self, device_name):
        """
        Retrieves the sensor states for a specific device, mapped to their global IDs.
        
        :param device_name: String - The name of the device (as defined in initialization).
        """
        if device_name in self.devices:
            esp = self.devices[device_name]
            status = {"name": esp.name, "ip": esp.ip, "data": {}}
            for k, v in esp.sensors.items():
                gid = int(k[1:]) + esp.offset_id
                status["data"][gid] = v
            return status
        return None
    
    def get_individual_actuators(self, device_name):
        """
        Retrieves the actuator states for a specific device mapped to global IDs.
        
        :param device_name: String - The name of the device.
        """
        if device_name in self.devices:
            esp = self.devices[device_name]
            data = {}
            for k, v in esp.actuators.items():
                gid = int(k[1:]) + esp.offset_id
                data[gid] = v
            return data
        return None

    def enable_general_sub(self):
        """Enables notification callbacks for every managed device."""
        for esp in self.devices.values(): esp.notifications_enabled = True

    def enable_exclusive_sub(self, device_name):
        """
        Enables notifications for a specific device while disabling all others.
        
        :param device_name: String - The name of the device to keep active.
        """
        if device_name in self.devices:
            for name, esp in self.devices.items():
                esp.notifications_enabled = (name == device_name)
            return True
        return False

    def disable_all_subs(self):
        """Disables notification callbacks for all managed devices."""
        for esp in self.devices.values(): esp.notifications_enabled = False

    def get_global_sensors(self):
        """Returns a sorted dictionary of all sensors across all devices using global IDs."""
        result = {}
        for gid, info in self.global_map.items():
            result[gid] = info['obj'].sensors[f's{info["local_id"]}']
        return dict(sorted(result.items()))
    
    def get_global_actuators(self):
        """Returns a sorted dictionary of all actuators across all devices using global IDs."""
        result = {}
        for gid, info in self.global_map.items():
            result[gid] = info['obj'].actuators[f'a{info["local_id"]}']
        return dict(sorted(result.items()))

    def set_global_actuator(self, global_id, state):
        """
        Updates the state of an actuator using its unique global ID.
        
        :param global_id: Integer - The unique global ID assigned to the actuator.
        :param state: Integer - The value (e.g., 0 or 1) to set.
        """
        if global_id in self.global_map:
            info = self.global_map[global_id]
            esp = info['obj']
            addr = esp._actuator_map.get(info['local_id'])
            if addr and esp.write_direct_register(addr, state):
                esp.actuators[f'a{info["local_id"]}'] = state
                return True
        return False

    def set_individual_actuator(self, device_name, local_id, state):
        """
        Updates a specific actuator on a named device using its local ID (1-7).
        
        :param device_name: String - The name of the device.
        :param local_id: Integer - The ID (1-7) of the actuator on that board.
        :param state: Integer - The value to set.
        """
        if device_name in self.devices:
            esp = self.devices[device_name]
            addr = esp._actuator_map.get(local_id)
            if addr and esp.write_direct_register(addr, state):
                esp.actuators[f'a{local_id}'] = state
                return True
        return False

    def disconnect_all(self):
        """Properly disconnects all ESP32 devices and stops all monitoring threads."""
        for esp in self.devices.values(): esp.disconnect()