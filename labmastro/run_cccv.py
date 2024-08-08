import csv
import time

from labmastro.power_supply.hanmatek.hm.instrument import HanmatekHmInstrument
from labmastro.power_supply.hanmatek.hm.control import HanmatekHmControl

SAMPLING_INTERVAL = 1 # seconds

def charge_battery(dc_control, max_voltage, initial_current, cutoff_current):
    # Open a CSV file to record voltage and current over time
    with open('charging_log.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Time', 'Voltage (V)', 'Current (A)'])  # Write the CSV headers

        # Step 1: Constant Current Phase
        dc_control.set_current(initial_current)  # Set the current limit
        dc_control.set_voltage(max_voltage)  # Set the maximum voltage to prevent overcharging
        dc_control.power_on()

        # Monitor until maximum voltage is reached
        while dc_control.get_voltage() < max_voltage:
            voltage = dc_control.get_voltage()
            current = dc_control.get_current()
            print(f"Charging... Voltage: {voltage} V, Current: {current} A")
            writer.writerow([int(time.time()*1000), voltage, current])
            time.sleep(SAMPLING_INTERVAL)

        # Step 2: Constant Voltage Phase
        while dc_control.get_current() > cutoff_current:
            voltage = dc_control.get_voltage()
            current = dc_control.get_current()
            print(f"Top-off... Voltage: {voltage} V, Current: {current} A")
            writer.writerow([int(time.time()*1000), voltage, current])
            time.sleep(SAMPLING_INTERVAL)

        dc_control.power_off()
        print("Charging complete.")

# Example of using the modified function
if __name__ == "__main__":
    instrument = HanmatekHmInstrument(port="/dev/ttyUSB0")
    dc_control = HanmatekHmControl(instrument)
    dc_control.set_over_voltage_protection(3.65*8 + 0.5)  # Set the over-voltage protection limit
    dc_control.set_over_current_protection(50)  # Set the over-current protection limit

    # Example parameters: max_voltage = 3.6V, initial_current = 5A, cutoff_current = 0.5A
    charge_battery(dc_control, 3.65*8, 5, 0.5)
