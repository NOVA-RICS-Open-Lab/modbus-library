from esp32_Modbus import MultiESP32Manager

def process_change(device_name, sensors, offset):
    print(f"\n[NOTIFICATION - {device_name}]")
    for k, v in sensors.items():
        gid = int(k[1:]) + offset
        print(f"  > Global ID {gid:02d} (Local {k}): {v}")
    print("command > ", end="", flush=True)

def configure_devices():
    configurations = []
    print("--- ESP32 Device Configuration ---")
    try:
        qty = int(input("How many ESP32 do you want to configure? ").strip() or 0)
        for i in range(qty):
            name = input(f"Name for ESP#{i+1}: ").strip()
            ip = input(f"IP Address for '{name}': ").strip()
            configurations.append({'name': name, 'ip': ip})
        return configurations
    except ValueError: return []

configs = configure_devices()
if not configs: exit()

manager = MultiESP32Manager(configs, callback_function=process_change)
connection_status = manager.connect_and_monitor()

for name, success in connection_status.items():
    print(f"[{name}] {'Connected' if success else 'Error'}")

print("\n--- COMMANDS ---")
print("gui                   - Open Graphical Monitor Window")
print("sensors               - View all sensors (Global)")
print("status_s [NAME]       - View ONLY sensors of a specific ESP")
print("status_a [NAME]       - View ONLY actuators of a specific ESP")
print("actuators             - View all actuators (Global)")
print("sub                   - Enable notifications for ALL devices")
print("sub [NAME]            - Enable EXCLUSIVE notifications for one device")
print("unsub                 - Mute all notifications")
print("set [GLOBAL_ID] [V]   - Control actuator by Global ID")
print("set_ind [NAME] [ID] [V]- Control actuator by Local ID")
print("exit                  - Terminate program")

try:
    while True:
        cmd = input("\ncommand > ").strip().split()
        if not cmd: continue
        action = cmd[0].lower()

        if action == 'exit': break
        
        elif action == 'gui':
            if not manager.open_ui(): print("UI is already open.")
            else: print("Opening UI...")

        elif action == 'sensors': print(manager.get_global_sensors())
        elif action == 'actuators': print(manager.get_global_actuators())
        elif action == 'status_s' and len(cmd)>1: print(manager.get_individual_sensors(cmd[1]))
        elif action == 'status_a' and len(cmd)>1: print(manager.get_individual_actuators(cmd[1]))
        elif action == 'sub':
            if len(cmd)==1: manager.enable_general_sub()
            else: manager.enable_exclusive_sub(cmd[1])
        elif action == 'unsub': manager.disable_all_subs()
        elif action == 'set' and len(cmd)>2:
            manager.set_global_actuator(int(cmd[1]), int(cmd[2]))
        elif action == 'set_ind' and len(cmd)>3:
            manager.set_individual_actuator(cmd[1], int(cmd[2]), int(cmd[3]))

except KeyboardInterrupt: pass
finally:
    manager.disconnect_all()
    print("\nShutdown complete.")