from esp32modbusV2 import MultiESP32Manager
import time

# Callback function to handle background notifications (keeping it silent for automation)
def silent_callback(device_name, sensors, offset):
    pass

def double_esp_automation():
    # 1. Configuration for 2 Devices
    # Global IDs: ESP_A (1-7), ESP_B (8-14)
    configs = [
        {'name': 'ESP_A', 'ip': '192.168.1.20'},
        {'name': 'ESP_B', 'ip': '192.168.1.21'}
    ]
    
    # 2. Initialize Manager
    manager = MultiESP32Manager(configs, callback_function=silent_callback)
    
    # 3. Connect and Start Monitoring
    connection_results = manager.connect_and_monitor()
    
    # Check if both are connected
    if not all(connection_results.values()):
        for name, success in connection_results.items():
            if not success:
                print(f"Error: Could not connect to {name}")
        return

    # Direct references to make the logic cleaner
    esp_a = manager.devices['ESP_A']
    esp_b = manager.devices['ESP_B']

    print("Both ESPs connected. Synchronizing...")
    time.sleep(1) # Wait for initial sync_all to complete

    print("Starting dual automation cycle...")
    
    try:
        while True:
            # STEP 1: Wait for Sensor 4 on ESP_A (Global ID 4)
            if esp_a.sensors['s4'] == 0:
                print("\n--- NEW CYCLE STARTED ---")
                print("[STEP 1] Sensor 4 on ESP_A detected item. Activating ESP_B Actuator 2 (Global ID 9).")
                manager.set_global_actuator(9, 1)
                
                # STEP 2: Wait for Sensor 1 on ESP_B (Global ID 8) to confirm action
                while esp_b.sensors['s4'] == 1:
                    time.sleep(0.1)
                
                print("[STEP 2] Sensor 1 on ESP_B active. ESP_B Act 2 OFF, ESP_A Act 1 (Global ID 1) ON.")
                manager.set_global_actuator(9, 0)
                manager.set_global_actuator(1, 1)

                # STEP 3: Wait for Sensor 1 on ESP_A (Global ID 1)
                while esp_a.sensors['s1'] == 0:
                    time.sleep(0.1)
                
                print("[STEP 3] Sensor 1 on ESP_A active. ESP_A Act 1 OFF, ESP_A Act 2 (Global ID 2) ON.")
                manager.set_global_actuator(1, 0)
                manager.set_global_actuator(2, 1)

                # STEP 4: Wait for Sensor 4 on ESP_B (Global ID 11)
                while esp_b.sensors['s1'] == 0:
                    time.sleep(0.1)
                
                print("[STEP 4] Sensor 4 on ESP_B active. ESP_A Act 2 OFF, ESP_B Act 1 (Global ID 8) ON.")
                manager.set_global_actuator(2, 0)
                manager.set_global_actuator(8, 1)

                # STEP 5: Wait for Sensor 4 on ESP_A to reset
                while esp_a.sensors['s4'] == 1:
                    time.sleep(0.1)

                print("[STEP 5] Sensor 4 on ESP_A released. ESP_B Act 1 OFF. Cycle Finished.")
                manager.set_global_actuator(8, 0)

                time.sleep(0.5)

            time.sleep(0.1) # Prevent high CPU usage

    except KeyboardInterrupt:
        print("\nAutomation stopped by user.")
    finally:
        # Emergency shutdown
        manager.disconnect_all()

if __name__ == "__main__":
    double_esp_automation()